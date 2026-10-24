import sys
from config import DEFAULT_EXCEL_PATH, DEFAULT_D_MAX, DEFAULT_V_MAX
from src.orquestrador import AgenteNablaOrchestrator


def main():
    print("============================================================")
    print("      AGENTE NΛBLΛ  - SISTEMA INTERATIVO DE AUDITORIA")
    print("============================================================\n")
    ruta_excel = input(
        f"Informe a rota do arquivo Excel [{DEFAULT_EXCEL_PATH}]: ").strip()
    if not ruta_excel:
        ruta_excel = DEFAULT_EXCEL_PATH
    d_max_input = input(
        f"Limite Deslocamento D_max mm [{DEFAULT_D_MAX}]: ").strip()
    d_max = float(d_max_input) if d_max_input else DEFAULT_D_MAX
    v_max_input = input(
        f"Limite Velocidade V_max mm/s [{DEFAULT_V_MAX}]: ").strip()
    v_max = float(v_max_input) if v_max_input else DEFAULT_V_MAX
    print("\n[INFO] Inicializando Orquestrador Multi-Agente e base RAG...")
    orquestador = AgenteNablaOrchestrator(
        ruta_excel, d_max=d_max, v_max=v_max)
    print("\n[INFO] Auditoria concluída com sucesso!")
    print("Digite suas perguntas ou 'sair' para encerrar a sessão.\n")
    # Primeira consulta automática
    primeira_consulta = "Gere o relatório executivo formal com a análise estrutural e enquadramento normativo."
    print(f"Usuário: {primeira_consulta}")
    print("-" * 60)
    resposta_inicial = orquestador.responder_consulta(primeira_consulta)
    print(f"\nAgente NΛBLΛ:\n{resposta_inicial}\n")
    print("=" * 60)
    # Bordo de interatividade contínua
    while True:
        try:
            entrada = input("\nSua consulta (ou 'sair'): ").strip()
            if entrada.lower() in ['salir', 'sair', 'exit', 'quit']:
                print("\n[INFO] Sessão encerrada.")
                break
            if not entrada:
                continue
            print("\n[NΛBLΛ processando...]")
            resposta = orquestador.responder_consulta(entrada)
            print(f"\nAgente NΛBLΛ:\n{resposta}")
            print("-" * 60)
        except KeyboardInterrupt:
            print("\n[INFO] Sessão interrompida.")
            break


if __name__ == "__main__":
    main()
