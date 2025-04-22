from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

app = FastAPI()

# Função para carregar os dados do arquivo JSON
def carregar_dados():
    with open("instituicoes.json", "r", encoding="utf-8") as file:
        return json.load(file)

# Função para salvar os dados no arquivo JSON
def salvar_dados(dados):
    with open("instituicoes.json", "w", encoding="utf-8") as file:
        json.dump(dados, file, ensure_ascii=False, indent=2)

# Modelo Pydantic para validação
class Instituicao(BaseModel):
    co_instituicao: int
    no_instituicao: str
    cidade: str
    uf: str
    dependencia_administrativa: str

# Carrega os dados da instituição
instituicoes_data = carregar_dados()

@app.get("/instituicoesensino")
def listar_instituicoes():
    return instituicoes_data

@app.get("/instituicoesensino/{co_instituicao}")
def recuperar_instituicao(co_instituicao: int):
    instituicao = next((inst for inst in instituicoes_data if inst["co_instituicao"] == co_instituicao), None)
    if instituicao is None:
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    return instituicao

@app.post("/instituicoesensino")
def inserir_instituicao(nova_instituicao: Instituicao):
    for inst in instituicoes_data:
        if inst["co_instituicao"] == nova_instituicao.co_instituicao:
            raise HTTPException(status_code=400, detail="Instituição já existe")
    instituicoes_data.append(nova_instituicao.dict())
    salvar_dados(instituicoes_data)
    return {"mensagem": "Instituição adicionada com sucesso"}

@app.put("/instituicoesensino")
def atualizar_instituicao(inst_atualizada: Instituicao):
    for i, inst in enumerate(instituicoes_data):
        if inst["co_instituicao"] == inst_atualizada.co_instituicao:
            instituicoes_data[i] = inst_atualizada.dict()
            salvar_dados(instituicoes_data)
            return {"mensagem": "Instituição atualizada com sucesso"}
    raise HTTPException(status_code=404, detail="Instituição não encontrada")

@app.delete("/instituicoesensino/{co_instituicao}")
def remover_instituicao(co_instituicao: int):
    for i, inst in enumerate(instituicoes_data):
        if inst["co_instituicao"] == co_instituicao:
            instituicoes_data.pop(i)
            salvar_dados(instituicoes_data)
            return {"mensagem": "Instituição removida com sucesso"}
    raise HTTPException(status_code=404, detail="Instituição não encontrada")
