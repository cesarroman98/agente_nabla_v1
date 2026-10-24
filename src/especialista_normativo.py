import os
from langchain_core.documents import Document


class AgenteEspecialistaNormativoRAG:
    """
    Agente 2: Motor RAG normativo real con ChromaDB, ingestión de PDFs técnicos
    (ABNT NBR 6123, ANSI/TIA-222-H) e recuperação vetorial por similaridade.
    """

    def __init__(self, pasta_db: str = "./db_normas", modelo_emb: str = "bge-m3"):
        self.pasta_db = pasta_db
        self.modelo_emb = modelo_emb
        self.db = None
        self.usar_chroma = False
        self._inicializar_db()

    def _inicializar_db(self):
        try:
            from langchain_chroma import Chroma
            from langchain_ollama import OllamaEmbeddings

            embeddings = OllamaEmbeddings(model=self.modelo_emb)
            self.db = Chroma(
                collection_name="normas",
                persist_directory=self.pasta_db,
                embedding_function=embeddings
            )
            self.usar_chroma = True
            print(
                "[INFO Agente 2 RAG] Base vetorial ChromaDB inicializada com sucesso.")
        except Exception as e:
            print(
                f"[Aviso RAG] ChromaDB ou Ollama Embeddings não disponível ({str(e)}). Usando modo fallback.")
            self.usar_chroma = False

    def ingerir_pdf(self, caminho_pdf: str, norma: str, tipo_estrutura: str = "torre", versao: str = "") -> int:
        """
        Ingere um arquivo PDF de norma técnica, dividindo em chunks de 800 caracteres com metadatos.
        """
        if not os.path.exists(caminho_pdf):
            print(
                f"[ERRO RAG Ingestão] O arquivo '{caminho_pdf}' não foi encontrado.")
            return 0

        try:
            from langchain_community.document_loaders import PyPDFLoader
            from langchain_text_splitters import RecursiveCharacterTextSplitter

            paginas = PyPDFLoader(caminho_pdf).load()
            # Reducido a 800 caracteres para melhor precisão de busca
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=800, chunk_overlap=150)
            chunks = text_splitter.split_documents(paginas)

            for c in chunks:
                c.metadata = {
                    "norma": norma,
                    "versao": versao,
                    "tipo_estrutura": tipo_estrutura,
                    "pagina": int(c.metadata.get("page", 0)) + 1
                }

            if not self.usar_chroma:
                self._inicializar_db()

            if self.db:
                self.db.add_documents(chunks)
                print(
                    f"[SUCCESS RAG] Ingeridos {len(chunks)} chunks da norma '{norma}' na base vetorial.")
                return len(chunks)
        except Exception as e:
            print(f"[ERRO RAG Ingestão] Falha ao processar PDF: {str(e)}")
            return 0

    def consultar(self, pergunta: str, tipo_estrutura: str = "torre", k: int = 5) -> str:
        """
        Realiza a busca vetorial por similaridade retornando até k=5 trechos com citação de página.
        """
        if self.usar_chroma and self.db:
            try:
                # Busca sin filtro rígido para garantir retorno do PDF
                docs = self.db.similarity_search(pergunta, k=k)
                if docs:
                    resultado = "FRAGMENTOS NORMATIVOS RECUPERADOS VETORIALMENTE DO PDF (RAG Real):\n\n"
                    for d in docs:
                        norma = d.metadata.get('norma', 'Norma Técnica')
                        versao = d.metadata.get('versao', '')
                        pagina = d.metadata.get('pagina', 1)
                        resultado += f"[{norma} {versao}, p. {pagina}]\n{d.page_content}\n\n"
                    return resultado
            except Exception as e:
                print(f"[Aviso RAG Busca Vetorial]: {str(e)}")

        # Fallback genérico transparente (sem citações falsas de páginas)
        return (
            "CONTEXTO NORMATIVO OPERACIONAL (Base do Sistema):\n\n"
            "- ABNT NBR 6123 / ANSI/TIA-222-H: Estabelecem limites operacionais de serviço para "
            "deslocamento horizontal, torção e vibração dinâmica no topo de torres de telecomunicações.\n"
            "- CRITÉRIO TÉCNICO NABLA SHM-STD-01: Limiares operacionais para auditoria: "
            "Normal (<85%), Advertência (85%-99% para manutenção preventiva) "
            "e Alerta Crítico (>=100% para inspeção presencial imediata)."
        )

    def recuperar_contexto(self, estado_global: str) -> str:
        """
        Query refinada para forçar contexto de torres e forças de vento.
        """
        query = "torre treliçada forças vento efeito dinâmico limites de serviço deformação"
        return self.consultar(pergunta=query, tipo_estrutura="torre", k=5)
