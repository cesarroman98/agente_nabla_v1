# ingestor_pdf.py
import os
from src.especialista_normativo import AgenteEspecialistaNormativoRAG


def ejecutar_ingestao():
    ruta_pdf = os.path.join("normas", "NBR6123.pdf")

    print(f"[INFO] Iniciando ingestión del documento: {ruta_pdf}")
    rag = AgenteEspecialistaNormativoRAG(
        pasta_db="./db_normas", modelo_emb="bge-m3")

    total_chunks = rag.ingerir_pdf(
        caminho_pdf=ruta_pdf,
        norma="ABNT NBR 6123",
        tipo_estrutura="torre",
        versao="1988"
    )

    if total_chunks > 0:
        print(
            f"✅ ¡Ingestión exitosa! Se guardaron {total_chunks} fragmentos en ChromaDB.")
    else:
        print("⚠️ No se pudieron generar fragmentos. Revisa si Ollama o los embeddings están activos.")


if __name__ == "__main__":
    ejecutar_ingestao()
