import csv
import json

csv_path = "microdados_ed_basica_2024.csv"
json_path = "instituicoes.json"

instituicoes = []

# Lê o arquivo CSV e converte para lista de dicionários
with open(csv_path, encoding="latin1") as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    for row in reader:
        instituicao = {
            "co_instituicao": int(row["CO_ENTIDADE"]),
            "no_instituicao": row["NO_ENTIDADE"],
            "cidade": row["NO_MUNICIPIO"],
            "uf": row["SG_UF"],
            "dependencia_administrativa": row["TP_DEPENDENCIA"]
        }
        instituicoes.append(instituicao)

# Salva os dados no arquivo JSON
with open(json_path, "w", encoding="utf-8") as jsonfile:
    json.dump(instituicoes, jsonfile, ensure_ascii=False, indent=2)

print(f"{len(instituicoes)} instituições salvas em {json_path}")
