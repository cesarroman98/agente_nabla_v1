from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from src.analista_numerico import ejecutar_analisis_numerico
from src.especialista_normativo import AgenteEspecialistaNormativoRAG
from config import OLLAMA_BASE_URL, MODEL_NAME


class AgenteNablaOrchestrator:
    """
    Agente 3 e Orquestador Principal: Integra o processamento do Analista Numérico,
    a recuperação do Agente RAG e a síntese via LLM com memória de sessão.
    """

    def __init__(self, ruta_excel: str, d_max: float = 0.50, v_max: float = 5.00):
        self.d_max = d_max
        self.v_max = v_max
        self.ruta_excel = ruta_excel

        # Execução dos Agentes 1 e 2
        self.datos_auditados = ejecutar_analisis_numerico(
            ruta_excel, d_max=d_max, v_max=v_max)
        self.agente_rag = AgenteEspecialistaNormativoRAG()
        self.contexto_rag = self.agente_rag.recuperar_contexto(
            self.datos_auditados["estado_global"])

        self.historial_memoria = []

        # Prompt com LangChain e suporte a Histórico
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """
Você é o Agente NΛBLΛ, um Engenheiro Especialista em Análise Estrutural de Torres de Telecomunicações.

# ESTADO GLOBAL DA ESTRUTURA:
{estado_global}

# DADOS AUDITADOS DO ARQUIVO EXCEL:
- Total de sensores analisados: {total_analisados}
- Total de sensores em estado de alerta/advertência: {total_alertas}
- Pico máximo global de deslocamento (D): {pico_d} mm (Limite configurado: {d_max} mm)
- Pico máximo global de velocidade (V): {pico_v} mm/s (Limite configurado: {v_max} mm/s)

# TABELA DOS CASOS MAIS CRÍTICOS (EXATA):
{tabela_markdown}

# CONTEXTO NORMATIVO E CRITÉRIOS OPERACIONAIS (RAG):
{contexto_rag}

# REGRAS RIGOROSAS DE RESPOSTA:
1. Responda ESTRITAMENTE em português técnico como um Engenheiro Auditor Estrutural.
2. NUNCA forneça passos ou instruções de como usar o software Microsoft Excel (ex: não diga "abra o Excel", "filtre as colunas", "pressione Enter").
3. NUNCA mencione a palavra "imagem" ou crie suposições de telas.
4. Responda DIRETAMENTE à pergunta do usuário utilizando APENAS os dados fornecidos na tabela acima. Por exemplo, se perguntarem em quais abas o sensor z27 teve picos graves, liste diretamente as planilhas (DATOS5, DATOS3, DATOS1) com seus respectivos valores.
5. Se o usuário solicitar um relatório executivo formal, estruture no formato:
   - Resumo Executivo (Estado global).
   - Tabela dos Casos Mais Críticos.
   - Enquadramento Normativo e Análise por Cotas Z.
   - Conclusões e Recomendações Técnicas de Manutenção.
"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input_usuario}")
        ])

        self.llm = Ollama(model=MODEL_NAME, base_url=OLLAMA_BASE_URL)
        self.chain = self.prompt_template | self.llm

    def responder_consulta(self, mensaje_usuario: str) -> str:
        # Correção do bug KeyError na chave tabela_markdown
        respuesta = self.chain.invoke({
            "estado_global": self.datos_auditados["estado_global"],
            "total_analisados": self.datos_auditados["total_analisados"],
            "total_alertas": self.datos_auditados["total_alertas"],
            "pico_d": self.datos_auditados["pico_d"],
            "pico_v": self.datos_auditados["pico_v"],
            "d_max": self.d_max,
            "v_max": self.v_max,
            "tabela_markdown": self.datos_auditados["tabela_markdown"],
            "contexto_rag": self.contexto_rag,
            "chat_history": self.historial_memoria,
            "input_usuario": mensaje_usuario
        })

        self.historial_memoria.append(HumanMessage(content=mensaje_usuario))
        self.historial_memoria.append(AIMessage(content=respuesta))

        return respuesta
