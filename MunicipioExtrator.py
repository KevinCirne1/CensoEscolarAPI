import requests
import sqlite3
import json

# Configurações
url = "https://servicodados.ibge.gov.br/api/v1/localidades/regioes/2/municipios"
db_path = "instituicoes.db"
json_path = "municipios_nordeste.json"

try:
    # Fazer a requisição à API
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Erro na requisição: Status {response.status_code}")
    
    # Extrair os dados JSON
    municipios = response.json()
    if not municipios:
        raise Exception("Nenhum dado retornado pela API")
    
    # Preparar dados para inserção
    municipios_db = [
        (
            m["id"],
            m["nome"],
            m["microrregiao"]["mesorregiao"]["UF"]["id"],
            m["microrregiao"]["id"],
            m["microrregiao"]["mesorregiao"]["id"]
        )
        for m in municipios
    ]
    
    # Conectar ao banco SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Criar tabela municipios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS municipios (
            id_municipio INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            id_estado INTEGER,
            id_microrregiao INTEGER,
            id_mesorregiao INTEGER,
            FOREIGN KEY (id_estado) REFERENCES estados(id_estado),
            FOREIGN KEY (id_microrregiao) REFERENCES microrregioes(id_microrregiao),
            FOREIGN KEY (id_mesorregiao) REFERENCES mesorregioes(id_mesorregiao)
        )
    """)
    
    # Inserir dados
    cursor.executemany("""
        INSERT OR REPLACE INTO municipios (id_municipio, nome, id_estado, id_microrregiao, id_mesorregiao)
        VALUES (?, ?, ?, ?, ?)
    """, municipios_db)
    
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM municipios")
    count = cursor.fetchone()[0]
    conn.close()
    
    # Salvar em JSON
    with open(json_path, "w", encoding="utf-8") as jsonfile:
        json.dump(municipios, jsonfile, ensure_ascii=False, indent=2)
    
    print(f"{len(municipios)} municípios extraídos da API")
    print(f"{count} municípios salvos no banco {db_path} (tabela 'municipios')")
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