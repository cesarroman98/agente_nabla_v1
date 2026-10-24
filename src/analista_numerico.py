import pandas as pd
import numpy as np


def ejecutar_analisis_numerico(ruta_excel: str, d_max: float = 0.50, v_max: float = 5.00) -> dict:
    """
    Agente 1: Convierte posições a deslocamentos relativos (Delta D = P(t) - P(0)),
    calcula picos de deformação e velocidade, e gera a tabela Markdown por % de Uso.
    """
    try:
        hojas = pd.read_excel(ruta_excel, header=None,
                              sheet_name=None, engine='openpyxl')
    except Exception as e:
        return {"error": f"Erro ao ler arquivo Excel: {str(e)}"}

    todos_sensores = []

    for nombre_hoja, df in hojas.items():
        for _, row in df.iterrows():
            sensor_str = str(row.iloc[0]).strip()
            sensor_upper = sensor_str.upper()

            if sensor_upper.startswith('Z') and len(sensor_upper) > 1:
                try:
                    num_sensor = int(sensor_upper.replace('Z', ''))
                except ValueError:
                    continue

                cota_nivel = (num_sensor + 1) // 2
                valores_raw = pd.to_numeric(
                    row.iloc[1:], errors='coerce').dropna()

                if valores_raw.empty:
                    continue

                # Distinción entre Deslocamento (Ímpar) y Velocidade (Par)
                if num_sensor % 2 != 0:
                    limite = d_max
                    tipo_var = "Deslocamento (D)"
                    # Conversão: Posição P(t) -> Deslocamento relativo Delta D = P(t) - P(0)
                    posicion_inicial = valores_raw.iloc[0]
                    valores_evaluar = valores_raw - posicion_inicial
                else:
                    limite = v_max
                    tipo_var = "Velocidade (V)"
                    valores_evaluar = valores_raw

                idx_pico = valores_evaluar.abs().idxmax()
                val_pico = valores_evaluar[idx_pico]
                pct_uso = (abs(val_pico) / limite) * 100.0

                if pct_uso >= 100.0:
                    estado = "ALERTA CRÍTICO"
                elif pct_uso >= 85.0:
                    estado = "ADVERTÊNCIA"
                else:
                    estado = "NORMAL"

                pct_exceso = ((abs(val_pico) - limite) / limite) * \
                    100.0 if pct_uso >= 100.0 else 0.0

                todos_sensores.append({
                    'Hoja': nombre_hoja,
                    'Sensor': sensor_upper.lower(),
                    'Tipo': tipo_var,
                    'Cota_Z': cota_nivel,
                    'Pico_Medido': round(float(val_pico), 3),
                    'Limite': limite,
                    'Uso_Pct': round(float(pct_uso), 1),
                    'Exceso_Pct': round(float(pct_exceso), 1),
                    'Estado': estado,
                    'Passo_Pico': str(idx_pico)
                })

    if not todos_sensores:
        return {
            "estado_global": "✅ NORMAL",
            "total_analisados": 0,
            "total_alertas": 0,
            "pico_d": 0.0,
            "pico_v": 0.0,
            "tabela_markdown": "Nenhum sensor válido encontrado no arquivo."
        }

    df_todos = pd.DataFrame(todos_sensores)

    alertas = df_todos[df_todos['Estado'].isin(
        ['ADVERTÊNCIA', 'ALERTA CRÍTICO'])].copy()
    alertas = alertas.sort_values(by='Uso_Pct', ascending=False)

    if (df_todos['Estado'] == 'ALERTA CRÍTICO').any():
        estado_global = "🚨 ALERTA CRÍTICO"
    elif (df_todos['Estado'] == 'ADVERTÊNCIA').any():
        estado_global = "⚠️ ADVERTÊNCIA"
    else:
        estado_global = "✅ NORMAL"

    top_5 = alertas.head(5) if not alertas.empty else df_todos.sort_values(
        by='Uso_Pct', ascending=False).head(5)

    tabela_markdown = "| Planilha/Caso | Sensor | Tipo | Cota Z (m) | Passo (Col) | Pico Medido | Limite | % Uso | % Excesso | Estado |\n"
    tabela_markdown += "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"

    for _, row in top_5.iterrows():
        tabela_markdown += f"| {row['Hoja']} | {row['Sensor']} | {row['Tipo']} | {row['Cota_Z']} | Passo {row['Passo_Pico']} | {row['Pico_Medido']} | {row['Limite']} | {row['Uso_Pct']}% | {row['Exceso_Pct']}% | {row['Estado']} |\n"

    d_mask = df_todos['Tipo'] == 'Deslocamento (D)'
    v_mask = df_todos['Tipo'] == 'Velocidade (V)'
    pico_d = float(
        df_todos[d_mask]['Pico_Medido'].abs().max()) if d_mask.any() else 0.0
    pico_v = float(
        df_todos[v_mask]['Pico_Medido'].abs().max()) if v_mask.any() else 0.0

    return {
        "estado_global": estado_global,
        "total_analisados": len(df_todos),
        "total_alertas": len(alertas),
        "pico_d": pico_d,
        "pico_v": pico_v,
        "tabela_markdown": tabela_markdown
    }
