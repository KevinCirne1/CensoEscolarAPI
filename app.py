from fastapi import FastAPI, HTTPException
import sqlite3

app = FastAPI()

DB_PATH = "instituicoes.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Para trazer como dicionário
    return conn

@app.get("/instituicoesensino")
def listar_instituicoes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM instituicoes")
    instituicoes = [dict(row) for row in cursor.fetchall()]    #fetchall pega todos os dados da lista
    conn.close()
    return instituicoes

@app.get("/instituicoesensino/{co_instituicao}")
def recuperar_instituicao(co_instituicao: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM instituicoes WHERE co_instituicao = ?", (co_instituicao,))
    instituicao = cursor.fetchone()    #pega apenas um regístro da lista
    conn.close()
    if instituicao:
        return dict(instituicao)
    raise HTTPException(status_code=404, detail="Instituição não encontrada")

@app.post("/instituicoesensino")
def inserir_instituicao(nova_instituicao: dict):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO instituicoes (co_instituicao, no_instituicao, cidade, uf, dependencia_administrativa)
            VALUES (?, ?, ?, ?, ?)
        """, (
            nova_instituicao["co_instituicao"],
            nova_instituicao["no_instituicao"],
            nova_instituicao["cidade"],
            nova_instituicao["uf"],
            nova_instituicao["dependencia_administrativa"]
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Instituição já existe")
    finally:
        conn.close()
    return {"mensagem": "Instituição adicionada com sucesso"}

@app.put("/instituicoesensino")
def atualizar_instituicao(inst_atualizada: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE instituicoes
        SET no_instituicao = ?, cidade = ?, uf = ?, dependencia_administrativa = ?
        WHERE co_instituicao = ?
    """, (
        inst_atualizada["no_instituicao"],
        inst_atualizada["cidade"],
        inst_atualizada["uf"],
        inst_atualizada["dependencia_administrativa"],
        inst_atualizada["co_instituicao"]
    ))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    conn.commit()
    conn.close()
    return {"mensagem": "Instituição atualizada com sucesso"}

@app.delete("/instituicoesensino/{co_instituicao}")
def remover_instituicao(co_instituicao: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM instituicoes WHERE co_instituicao = ?", (co_instituicao,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    conn.commit()
    conn.close()
    return {"mensagem": "Instituição removida com sucesso"}
