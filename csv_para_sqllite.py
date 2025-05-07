import csv
import sqlite3

# Caminhos dos arquivos
csv_path = "microdados_ed_basica_2024.csv"
db_path = "instituicoes.db"

# Conectar/criar banco de dados
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS instituicoes (
    co_instituicao INTEGER PRIMARY KEY,
    no_instituicao TEXT,
    cidade TEXT,
    uf TEXT,
    dependencia_administrativa TEXT
)
""")

# Ler o CSV e inserir apenas dados da Paraíba (UF = PB)
with open(csv_path, encoding="latin1") as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    instituicoes_pb = []
    for row in reader:
        if row["SG_UF"] == "PB":
            instituicao = (
                int(row["CO_ENTIDADE"]),
                row["NO_ENTIDADE"],
                row["NO_MUNICIPIO"],
                row["SG_UF"],
                row["TP_DEPENDENCIA"]
            )
            instituicoes_pb.append(instituicao)

# Inserir dados no banco
cursor.executemany("""
INSERT OR REPLACE INTO instituicoes (co_instituicao, no_instituicao, cidade, uf, dependencia_administrativa)
VALUES (?, ?, ?, ?, ?)
""", instituicoes_pb)

# Confirmar e fechar
conn.commit()
conn.close()

print(f"{len(instituicoes_pb)} instituições da Paraíba salvas no banco de dados {db_path}.")
