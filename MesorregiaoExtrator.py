import requests
import sqlite3
import json

# Configurações
url = "https://servicodados.ibge.gov.br/api/v1/localidades/regioes/2/mesorregioes"
db_path = "instituicoes.db"
json_path = "mesorregioes_nordeste.json"

try:
    # Fazer a requisição à API
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Erro na requisição: Status {response.status_code}")
    
    # Extrair os dados JSON
    mesorregioes = response.json()
    if not mesorregioes:
        raise Exception("Nenhum dado retornado pela API")
    
    # Preparar dados para inserção
    mesorregioes_db = [
        (
            m["id"],
            m["nome"],
            m["UF"]["id"]
        )
        for m in mesorregioes
    ]
    
    # Conectar ao banco SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Criar tabela mesorregioes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mesorregioes (
            id_mesorregiao INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            id_estado INTEGER,
            FOREIGN KEY (id_estado) REFERENCES estados(id_estado)
        )
    """)
    
    # Inserir dados
    cursor.executemany("""
        INSERT OR REPLACE INTO mesorregioes (id_mesorregiao, nome, id_estado)
        VALUES (?, ?, ?)
    """, mesorregioes_db)
    
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM mesorregioes")
    count = cursor.fetchone()[0]
    conn.close()
    
    # Salvar em JSON
    with open(json_path, "w", encoding="utf-8") as jsonfile:
        json.dump(mesorregioes, jsonfile, ensure_ascii=False, indent=2)
    
    print(f"{len(mesorregioes)} mesorregiões extraídas da API")
    print(f"{count} mesorregiões salvas no banco {db_path} (tabela 'mesorregioes')")
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