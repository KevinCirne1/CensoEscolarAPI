import requests
import sqlite3
import json

# Configurações
url = "https://servicodados.ibge.gov.br/api/v1/localidades/regioes/2/microrregioes"
db_path = "instituicoes.db"
json_path = "microrregioes_nordeste.json"

try:
    # Fazer a requisição à API
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Erro na requisição: Status {response.status_code}")
    
    # Extrair os dados JSON
    microrregioes = response.json()
    if not microrregioes:
        raise Exception("Nenhum dado retornado pela API")
    
    # Preparar dados para inserção
    microrregioes_db = [
        (
            m["id"],
            m["nome"],
            m["mesorregiao"]["id"]
        )
        for m in microrregioes
    ]
    
    # Conectar ao banco SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Criar tabela microrregioes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS microrregioes (
            id_microrregiao INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            id_mesorregiao INTEGER,
            FOREIGN KEY (id_mesorregiao) REFERENCES mesorregioes(id_mesorregiao)
        )
    """)
    
    # Inserir dados
    cursor.executemany("""
        INSERT OR REPLACE INTO microrregioes (id_microrregiao, nome, id_mesorregiao)
        VALUES (?, ?, ?)
    """, microrregioes_db)
    
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM microrregioes")
    count = cursor.fetchone()[0]
    conn.close()
    
    # Salvar em JSON
    with open(json_path, "w", encoding="utf-8") as jsonfile:
        json.dump(microrregioes, jsonfile, ensure_ascii=False, indent=2)
    
    print(f"{len(microrregioes)} microrregiões extraídas da API")
    print(f"{count} microrregiões salvas no banco {db_path} (tabela 'microrregioes')")
    print(f"Dados também salvos em {json_path}")
    
except requests.RequestException as e:
    print(f"Erro na conexão com a API: {e}")
except sqlite3.Error as e:
    print(f"Erro no banco de dados: {e}")
except json.JSONDecodeError as e:
    print(f"Erro ao processar o JSON: {e}")
except KeyError as e:
    print(f"Erro na estrutura do JSON: Campo {e} não encontrado")
except Exception as e:
    print(f"Erro: {e}")