import requests
import sqlite3
import json

# Configurações
url = "https://servicodados.ibge.gov.br/api/v1/localidades/regioes/2/estados"
db_path = "instituicoes.db"
json_path = "estados_nordeste.json"

try:
    # Fazer a requisição à API
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Erro na requisição: Status {response.status_code}")
    
    # Extrair os dados JSON
    estados = response.json()
    if not estados:
        raise Exception("Nenhum dado retornado pela API")
    
    # Preparar dados para inserção
    estados_db = [
        (
            e["id"],
            e["sigla"],
            e["nome"]
        )
        for e in estados
    ]
    
    # Conectar ao banco SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Criar tabela estados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estados (
            id_estado INTEGER PRIMARY KEY,
            sigla TEXT NOT NULL,
            nome TEXT NOT NULL
        )
    """)
    
    # Inserir dados
    cursor.executemany("""
        INSERT OR REPLACE INTO estados (id_estado, sigla, nome)
        VALUES (?, ?, ?)
    """, estados_db)
    
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM estados")
    count = cursor.fetchone()[0]
    conn.close()
    
    # Salvar em JSON
    with open(json_path, "w", encoding="utf-8") as jsonfile:
        json.dump(estados, jsonfile, ensure_ascii=False, indent=2)
    
    print(f"{len(estados)} estados extraídos da API")
    print(f"{count} estados salvos no banco {db_path} (tabela 'estados')")
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