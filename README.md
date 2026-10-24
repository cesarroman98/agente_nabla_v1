# 🛰️ AGENTE NABLA - Sistema Inteligente de Auditoria Estrutural 

O **Agente NABLA** é uma solução multi-agente baseada em IA e RAG (Retrieval-Augmented Generation) projetada para auditar a integridade estrutural de torres de telecomunicações e silos submetidas a cargas dinâmicas em conformidade com as normas.

---

## 🏗️ Fluxo e Arquitetura do Sistema

```
[ Arquivo Excel ] ──> [ Agente 1: Analista Numérico ] ──┐
                                                      ├──> [ Agente 3: Orquestrador LLM ] ──> [ Relatório / Chat ]
[ PDF Norma ] ──────> [ Agente 2: RAG Vetorial ] ─────┘
```

### 1. Entradas (Inputs)
- **Telemetria Estrutural (Excel):** Arquivo `.xlsx` contendo séries temporais de sensores organizados por cotas $Z$:
  - **Canais Ímperes ($z_1, z_3, \dots$):** Posição espacial horizontal $P(t)$ em mm.
  - **Canais Pares ($z_2, z_4, \dots$):** Velocidade de vibração $V(t)$ em mm/s.
- **Parâmetros Operacionais (Configuração/Console):**
  - $D_{\text{max}}$: Limite de deslocamento limite em mm (Padrão: $25.00\text{ mm}$ segundo critério ELS $H/500$).
  - $V_{\text{max}}$: Limite de velocidade de vibração em mm/s (Padrão: $5.00\text{ mm/s}$).
- **Base Normativa (PDF):** Norma **ABNT NBR 6123** para validação dos parâmetros aerodinâmicos e critérios operacionais internos.

---

### 2. Lógica de Processamento

1. **Conversão Física de Telemetria (Agente 1 - `analista_numerico.py`):**
   - Transforma a posição bruta $P(t)$ em **deslocamento relativo dinâmico ($\Delta D$)** eliminando o offset inicial de montagem:
     $$\Delta D(t) = P(t) - P(0)$$
   - Identifica o pico absoluto do sinal e calcula a porcentagem de utilização em relação aos limites de serviço:
     $$\% \text{ Uso} = \left( \frac{|\Delta D_{\text{pico}}|}{D_{\text{max}}} \right) \times 100$$
   - Classifica o estado do sensor:
     - **NORMAL:** $< 85\%$ de utilização.
     - **ADVERTÊNCIA:** $85\%$ a $99.9\%$ de utilização.
     - **ALERTA CRÍTICO:** $\ge 100\%$ de utilização.

2. **Recuperação Vetorial Normativa (Agente 2 - `especialista_normativo.py`):**
   - Ingestão do PDF normativo dividida em fragmentos com metadados de página.
   - Consulta vetorial (embeddings via Ollama) para recuperar os trechos exatos referentes a limites de serviço, fatores de vento ($V_k, S_1, S_2, S_3$) e fadiga.

3. **Síntese e Memória Conversacional (Agente 3 - `orquestrador.py`):**
   - Integra os dados numéricos auditados e os trechos normativos em um prompt estruturado.
   - Processa a resposta usando o modelo `llama3.2`.
   - Mantém o histórico de contexto (`chat_history`) para consultas consecutivas em tempo real.

---

### 3. Saídas (Outputs)
- **Estado Global Estrutural:** Diagnóstico em alto nível (`🚨 ALERTA CRÍTICO`, `⚠️ ADVERTÊNCIA`, `✅ NORMAL`).
- **Tabela Ordenada de Casos Críticos:** Ranking Markdown dos 5 sensores com maior taxa de utilização, indicando Planilha, Sensor, Cota $Z$, Passo temporal, Pico medido, Limite, % Uso e Estado.
- **Relatório Executivo Formal:** Documento estruturado com síntese executiva, enquadramento normativo ABNT/TIA e recomendações técnicas de manutenção presencial.
- **Interface Conversacional Interativa:** Respostas em tempo real para auditoria detalhada via terminal.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Python 3.10+
- [Ollama](https://ollama.com/) com o modelo `llama3.2` carregado.

### Instalação
```bash
# Clone o repositório
git clone [https://github.com/SEU_USUARIO/agente-nabla.git](https://github.com/SEU_USUARIO/agente-nabla.git)
cd agente-nabla/Agente_Nabla_v1.1

# Instale as dependências
pip install -r requirements.txt
```

### Execução
```bash
# 1. Ingestão opcional da norma em ChromaDB (executar apenas 1 vez)
python ingestor_pdf.py

# 2. Executar o sistema de auditoria interativo
python main.py
```