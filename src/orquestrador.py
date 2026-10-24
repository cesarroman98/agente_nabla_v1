from langchain_ollama import OllamaLLM
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
Você é o Agente NΛBLΛ, Engenheiro Especialista em Auditoria Estrutural de Torres de Telecomunicações.

# ESTADO GLOBAL DA ESTRUTURA:
{estado_global}

# DADOS AUDITADOS DO EXCEL:
- Sensores analisados: {total_analisados} | Alertas: {total_alertas}
- Pico D: {pico_d} mm (Limite: {d_max} mm) | Pico V: {pico_v} mm/s (Limite: {v_max} mm/s)

# TABELA DOS CASOS MAIS CRÍTICOS:
{tabela_markdown}

# CONTEXTO NORMATIVO RECUPERADO (RAG):
{contexto_rag}

# REGRAS RÍGIDAS DE RESPOSTA (ANTI-ALUCINAÇÃO):
1. Responda APENAS com base nos dados numéricos e nos textos do CONTEXTO NORMATIVO acima.
2. NUNCA invente seções, itens, capítulos ou citações entre aspas que não existam no texto do RAG.
3. Se o RAG não trouxer um capítulo ou seção solicitada pelo usuário, responda EXATAMENTE:
   "Essa seção específica não está disponível nos trechos recuperados do documento normativo."
4. NUNCA sugira soluções técnicas absurdas (como 'sistemas de ventilação ou controle de vento'). Recomende apenas inspeção estrutural presencial, reaperto de conexões e alinhamento de antenas.
5. NUNCA forneça passos sobre como usar o Microsoft Excel.
"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input_usuario}")
        ])

        self.llm = OllamaLLM(
            model=MODEL_NAME, base_url=OLLAMA_BASE_URL, temperature=0.0)
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
