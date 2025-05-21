import sqlite3

db_path = "instituicoes.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Criar tabela temporária com nova estrutura
    cursor.execute("""
        CREATE TABLE instituicoes_new (
            co_instituicao INTEGER PRIMARY KEY,
            no_instituicao TEXT NOT NULL,
            id_municipio INTEGER,
            id_estado INTEGER,
            id_mesorregiao INTEGER,
            id_microrregiao INTEGER,
            dependencia_administrativa TEXT,
            FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio),
            FOREIGN KEY (id_estado) REFERENCES estados(id_estado),
            FOREIGN KEY (id_mesorregiao) REFERENCES mesorregioes(id_mesorregiao),
            FOREIGN KEY (id_microrregiao) REFERENCES microrregioes(id_microrregiao)
        )
    """)

    # Migrar dados
    cursor.execute("""
        INSERT INTO instituicoes_new (
            co_instituicao, no_instituicao, id_municipio, id_estado, id_mesorregiao, id_microrregiao, dependencia_administrativa
        )
        SELECT 
            i.co_instituicao,
            i.no_instituicao,
            m.id_municipio,
            e.id_estado,
            m.id_mesorregiao,
            m.id_microrregiao,
            i.dependencia_administrativa
        FROM instituicoes i
        JOIN municipios m ON i.cidade = m.nome AND i.uf = m.uf
        JOIN estados e ON i.uf = e.sigla
    """)

    # Remover tabela antiga e renomear nova
    cursor.execute("DROP TABLE instituicoes")
    cursor.execute("ALTER TABLE instituicoes_new RENAME TO instituicoes")

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM instituicoes")
    count = cursor.fetchone()[0]
    print(f"{count} instituições migradas com sucesso")
    conn.close()

except sqlite3.Error as e:
    print(f"Erro no banco de dados: {e}")
finally:
    conn.close()