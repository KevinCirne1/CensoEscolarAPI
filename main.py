# ~/Downloads/pweb2/main.py
from fastapi import HTTPException
from marshmallow import Schema, fields, validates, ValidationError, validate
from app_config import create_app
from database import execute_query
import sqlite3

app = create_app()

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
        result = execute_query(
            "SELECT id_estado FROM estados WHERE id_estado = ?",
            (value,),
            fetch_one=True
        )
        if not result:
            raise ValidationError("ID de estado inválido.")

    @validates("id_municipio")
    def validate_id_municipio(self, value):
        result = execute_query(
            "SELECT id_municipio FROM municipios WHERE id_municipio = ? AND id_estado = ?",
            (value, self.context.get("id_estado")),
            fetch_one=True
        )
        if not result:
            raise ValidationError("ID de município inválido ou não pertence ao estado informado.")

    @validates("id_mesorregiao")
    def validate_id_mesorregiao(self, value):
        result = execute_query(
            "SELECT id_mesorregiao FROM mesorregioes WHERE id_mesorregiao = ? AND id_estado = ?",
            (value, self.context.get("id_estado")),
            fetch_one=True
        )
        if not result:
            raise ValidationError("ID de mesorregião inválido ou não pertence ao estado informado.")

    @validates("id_microrregiao")
    def validate_id_microrregiao(self, value):
        result = execute_query(
            "SELECT id_microrregiao FROM microrregioes WHERE id_microrregiao = ? AND id_mesorregiao = ?",
            (value, self.context.get("id_mesorregiao")),
            fetch_one=True
        )
        if not result:
            raise ValidationError("ID de microrregião inválido ou não pertence à mesorregião informada.")

@app.get("/instituicoesensino")
def listar_instituicoes():
    results = execute_query(
        """
        SELECT i.co_instituicao, i.no_instituicao, m.nome as cidade, e.sigla as uf, 
               mes.nome as mesorregiao, mic.nome as microrregiao, i.dependencia_administrativa
        FROM instituicoes i
        JOIN municipios m ON i.id_municipio = m.id_municipio
        JOIN estados e ON i.id_estado = e.id_estado
        JOIN mesorregioes mes ON i.id_mesorregiao = mes.id_mesorregiao
        JOIN microrregioes mic ON i.id_microrregiao = mic.id_microrregiao
        """,
        fetch_all=True
    )
    return [dict(row) for row in results]

@app.get("/instituicoesensino/{co_instituicao}")
def recuperar_instituicao(co_instituicao: int):
    result = execute_query(
        """
        SELECT i.co_instituicao, i.no_instituicao, m.nome as cidade, e.sigla as uf, 
               mes.nome as mesorregiao, mic.nome as microrregiao, i.dependencia_administrativa
        FROM instituicoes i
        JOIN municipios m ON i.id_municipio = m.id_municipio
        JOIN estados e ON i.id_estado = e.id_estado
        JOIN mesorregioes mes ON i.id_mesorregiao = mes.id_mesorregiao
        JOIN microrregioes mic ON i.id_microrregiao = mic.id_microrregiao
        WHERE i.co_instituicao = ?
        """,
        (co_instituicao,),
        fetch_one=True
    )
    if result:
        return dict(result)
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

    try:
        execute_query(
            """
            INSERT INTO instituicoes (co_instituicao, no_instituicao, id_municipio, id_estado, id_mesorregiao, id_microrregiao, dependencia_administrativa)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                validated_data["co_instituicao"],
                validated_data["no_instituicao"],
                validated_data["id_municipio"],
                validated_data["id_estado"],
                validated_data["id_mesorregiao"],
                validated_data["id_microrregiao"],
                validated_data["dependencia_administrativa"]
            )
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Instituição já existe ou IDs inválidos")
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

    rowcount = execute_query(
        """
        UPDATE instituicoes
        SET no_instituicao = ?, id_municipio = ?, id_estado = ?, id_mesorregiao = ?, id_microrregiao = ?, dependencia_administrativa = ?
        WHERE co_instituicao = ?
        """,
        (
            validated_data["no_instituicao"],
            validated_data["id_municipio"],
            validated_data["id_estado"],
            validated_data["id_mesorregiao"],
            validated_data["id_microrregiao"],
            validated_data["dependencia_administrativa"],
            validated_data["co_instituicao"]
        )
    )
    if rowcount == 0:
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    return {"mensagem": "Instituição atualizada com sucesso"}

@app.delete("/instituicoesensino/{co_instituicao}")
def remover_instituicao(co_instituicao: int):
    rowcount = execute_query(
        "DELETE FROM instituicoes WHERE co_instituicao = ?",
        (co_instituicao,)
    )
    if rowcount == 0:
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    return {"mensagem": "Instituição removida com sucesso"}

@app.get("/estados/nordeste")
def listar_estados_nordeste():
    results = execute_query(
        "SELECT id_estado, sigla, nome FROM estados",
        fetch_all=True
    )
    return [dict(row) for row in results]

@app.get("/municipios/nordeste")
def listar_municipios_nordeste(id_estado: int = None):
    query = "SELECT id_municipio, nome, id_estado FROM municipios"
    params = ()
    if id_estado:
        query += " WHERE id_estado = ?"
        params = (id_estado,)
    results = execute_query(query, params, fetch_all=True)
    return [dict(row) for row in results]

@app.get("/mesorregioes/nordeste")
def listar_mesorregioes_nordeste(id_estado: int = None):
    query = "SELECT id_mesorregiao, nome, id_estado FROM mesorregioes"
    params = ()
    if id_estado:
        query += " WHERE id_estado = ?"
        params = (id_estado,)
    results = execute_query(query, params, fetch_all=True)
    return [dict(row) for row in results]

@app.get("/microrregioes/nordeste")
def listar_microrregioes_nordeste(id_mesorregiao: int = None):
    query = "SELECT id_microrregiao, nome, id_mesorregiao FROM microrregioes"
    params = ()
    if id_mesorregiao:
        query += " WHERE id_mesorregiao = ?"
        params = (id_mesorregiao,)
    results = execute_query(query, params, fetch_all=True)
    return [dict(row) for row in results]
