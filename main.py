from fastapi import FastAPI, HTTPException
import sqlite3
from marshmallow import Schema, fields, validates, ValidationError, validate

app = FastAPI()

DB_PATH = "instituicoes.db"

# Função auxiliar para conexão com o banco
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Schema Marshmallow para validação
class InstituicaoSchema(Schema):
    co_instituicao = fields.Integer(required=True, validate=validate.Range(min=1))
    no_instituicao = fields.String(required=True, validate=validate.Length(min=1))
    id_municipio = fields.Integer(required=True, validate=validate.Range(min=1))
    id_estado = fields.Integer(required=True, validate=validate.Range(min=1))
    id_mesorregiao = fields.Integer(required=True, validate=validate.Range(min=1))
    id_microrregiao = fields.Integer(required=True, validate=validate.Range(min=1))
    dependencia_administrativa = fields.String(
        required=True,
        validate=validate.OneOf(["Federal", "Estadual", "Municipal", "Privada"])
    )

    @validates("id_estado")
    def validate_id_estado(self, value):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_estado FROM estados WHERE id_estado = ?", (value,))
        if not cursor.fetchone():
            conn.close()
            raise ValidationError("ID de estado inválido.")
        conn.close()

    @validates("id_municipio")
    def validate_id_municipio(self, value):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_municipio FROM municipios WHERE id_municipio = ? AND id_estado = ?", 
                      (value, self.context.get("id_estado")))
        if not cursor.fetchone():
            conn.close()
            raise ValidationError("ID de município inválido ou não pertence ao estado informado.")
        conn.close()

    @validates("id_mesorregiao")
    def validate_id_mesorregiao(self, value):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_mesorregiao FROM mesorregioes WHERE id_mesorregiao = ? AND id_estado = ?", 
                      (value, self.context.get("id_estado")))
        if not cursor.fetchone():
            conn.close()
            raise ValidationError("ID de mesorregião inválido ou não pertence ao estado informado.")
        conn.close()

    @validates("id_microrregiao")
    def validate_id_microrregiao(self, value):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_microrregiao FROM microrregioes WHERE id_microrregiao = ? AND id_mesorregiao = ?", 
                      (value, self.context.get("id_mesorregiao")))
        if not cursor.fetchone():
            conn.close()
            raise ValidationError("ID de microrregião inválido ou não pertence à mesorregião informada.")
        conn.close()

@app.get("/instituicoesensino")
def listar_instituicoes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.co_instituicao, i.no_instituicao, m.nome as cidade, e.sigla as uf, 
               mes.nome as mesorregiao, mic.nome as microrregiao, i.dependencia_administrativa
        FROM instituicoes i
        JOIN municipios m ON i.id_municipio = m.id_municipio
        JOIN estados e ON i.id_estado = e.id_estado
        JOIN mesorregioes mes ON i.id_mesorregiao = mes.id_mesorregiao
        JOIN microrregioes mic ON i.id_microrregiao = mic.id_microrregiao
    """)
    instituicoes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return instituicoes

@app.get("/instituicoesensino/{co_instituicao}")
def recuperar_instituicao(co_instituicao: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.co_instituicao, i.no_instituicao, m.nome as cidade, e.sigla as uf, 
               mes.nome as mesorregiao, mic.nome as microrregiao, i.dependencia_administrativa
        FROM instituicoes i
        JOIN municipios m ON i.id_municipio = m.id_municipio
        JOIN estados e ON i.id_estado = e.id_estado
        JOIN mesorregioes mes ON i.id_mesorregiao = mes.id_mesorregiao
        JOIN microrregioes mic ON i.id_microrregiao = mic.id_microrregiao
        WHERE i.co_instituicao = ?
    """, (co_instituicao,))
    instituicao = cursor.fetchone()
    conn.close()
    if instituicao:
        return dict(instituicao)
    raise HTTPException(status_code=404, detail="Instituição não encontrada")

@app.post("/instituicoesensino")
def inserir_instituicao(nova_instituicao: dict):
    schema = InstituicaoSchema()
    try:
        validated_data = schema.load(nova_instituicao, context={
            "id_estado": nova_instituicao.get("id_estado"),
            "id_mesorregiao": nova_instituicao.get("id_mesorregiao"),
            "id_microrregiao": nova_instituicao.get("id_microrregiao")
        })
    except ValidationError as err:
        raise HTTPException(status_code=422, detail=err.messages)

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO instituicoes (co_instituicao, no_instituicao, id_municipio, id_estado, id_mesorregiao, id_microrregiao, dependencia_administrativa)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            validated_data["co_instituicao"],
            validated_data["no_instituicao"],
            validated_data["id_municipio"],
            validated_data["id_estado"],
            validated_data["id_mesorregiao"],
            validated_data["id_microrregiao"],
            validated_data["dependencia_administrativa"]
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Instituição já existe ou IDs inválidos")
    finally:
        conn.close()
    return {"mensagem": "Instituição adicionada com sucesso"}

@app.put("/instituicoesensino")
def atualizar_instituicao(inst_atualizada: dict):
    schema = InstituicaoSchema()
    try:
        validated_data = schema.load(inst_atualizada, context={
            "id_estado": inst_atualizada.get("id_estado"),
            "id_mesorregiao": inst_atualizada.get("id_mesorregiao"),
            "id_microrregiao": inst_atualizada.get("id_microrregiao")
        })
    except ValidationError as err:
        raise HTTPException(status_code=422, detail=err.messages)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE instituicoes
        SET no_instituicao = ?, id_municipio = ?, id_estado = ?, id_mesorregiao = ?, id_microrregiao = ?, dependencia_administrativa = ?
        WHERE co_instituicao = ?
    """, (
        validated_data["no_instituicao"],
        validated_data["id_municipio"],
        validated_data["id_estado"],
        validated_data["id_mesorregiao"],
        validated_data["id_microrregiao"],
        validated_data["dependencia_administrativa"],
        validated_data["co_instituicao"]
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

@app.get("/estados/nordeste")
def listar_estados_nordeste():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_estado, sigla, nome FROM estados")
    estados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return estados

@app.get("/municipios/nordeste")
def listar_municipios_nordeste(id_estado: int = None):
    conn = get_connection()
    cursor = conn.cursor()
    if id_estado:
        cursor.execute("SELECT id_municipio, nome, id_estado FROM municipios WHERE id_estado = ?", (id_estado,))
    else:
        cursor.execute("SELECT id_municipio, nome, id_estado FROM municipios")
    municipios = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return municipios

@app.get("/mesorregioes/nordeste")
def listar_mesorregioes_nordeste(id_estado: int = None):
    conn = get_connection()
    cursor = conn.cursor()
    if id_estado:
        cursor.execute("SELECT id_mesorregiao, nome, id_estado FROM mesorregioes WHERE id_estado = ?", (id_estado,))
    else:
        cursor.execute("SELECT id_mesorregiao, nome, id_estado FROM mesorregioes")
    mesorregioes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return mesorregioes

@app.get("/microrregioes/nordeste")
def listar_microrregioes_nordeste(id_mesorregiao: int = None):
    conn = get_connection()
    cursor = conn.cursor()
    if id_mesorregiao:
        cursor.execute("SELECT id_microrregiao, nome, id_mesorregiao FROM microrregioes WHERE id_mesorregiao = ?", (id_mesorregiao,))
    else:
        cursor.execute("SELECT id_microrregiao, nome, id_mesorregiao FROM microrregioes")
    microrregioes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return microrregioes