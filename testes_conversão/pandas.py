import pandas as pd
import json

# Função: Excel para JSON
def excel_para_json(caminho_excel: str) -> str:
    df = pd.read_excel(caminho_excel, engine="openpyxl")
    return df.to_json(orient="records", force_ascii=False, indent=4)

# Função: JSON para Excel
def json_para_excel(caminho_json: str, caminho_excel: str):
    with open(caminho_json, "r", encoding="utf-8") as f:
        dados = json.load(f)
    df = pd.DataFrame(dados)
    df.to_excel(caminho_excel, index=False)

# ===== Exemplo de uso =====
if __name__ == "__main__":
    # Excel para JSON
    json_str = excel_para_json("registro.xlsx")
    with open("registro.json", "w", encoding="utf-8") as f:
        f.write(json_str)
    print("Excel convertido para JSON: registro.json")

    # JSON de volta para Excel
    json_para_excel("registro.json", "registro_de_json.xlsx")
    print("JSON convertido de volta para Excel: registro_de_json.xlsx")
