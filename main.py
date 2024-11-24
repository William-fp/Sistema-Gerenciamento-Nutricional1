from http import HTTPStatus
from fastapi import FastAPI, HTTPException, UploadFile, File
from models import Usuario, Refeicao, Alimento
import csv
import os
import io
from pydantic import BaseModel
import zipfile
import hashlib

app = FastAPI()

usuarios: list[Usuario] = []
alimentos: list[Alimento] = []


class CSV(BaseModel):
  data: list[Alimento]
  file_name: str


@app.get("/")
def padrao(): 
  return {"msg": "Bem vindo ao Sistema de Gestão Nutricional."}

# CRIAR UM USUARIO

@app.post("/usuarios/")
def criar_usuario(usuario: Usuario) -> Usuario:
  if any(usuario_atual.id == usuario.id for usuario_atual in usuarios):
    raise HTTPException(status_code=400, detail="ID existente.")
  usuarios.append(usuario)
  return usuario

# LISTAR TODOS OS USUARIOS

@app.get("/usuarios/")
def listar_usuarios() -> list[Usuario]:
  return usuarios

# LISTAR UM USUARIO ESPECIFICO

@app.get("/usuarios/{usuario_id}")
def ler_usuario(usuario_id: int) -> Usuario:
  for usuario in usuarios:
    if usuario.id == usuario_id:
      return usuario
  raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Usuário não encontrado.")

# ATUALIZAR UM USUARIO

@app.put("/usuarios/{usuario_id}")
def atualizar_usuario(usuario_id: int, usuario_att: Usuario) -> Usuario:
  for i, usuario in enumerate(usuarios):
    if usuario.id == usuario_id:
      if usuario_att.id != usuario_id:
        usuario_att.id = usuario_id
      usuarios[i] = usuario_att
      return usuario_att
  raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Usuário não encontrado.")
  
# DELETAR UM USUARIO

@app.delete("/usuarios/{usuario_id}")
def remover_usuario(usuario_id: int):
    for usuario in usuarios:
        if usuario.id == usuario_id:
            usuarios.remove(usuario)
            return {"msg": "Usuário removido."}
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Usuário não encontrado.")


# CRIAR UMA REFEICAO PARA UM USUARIO

@app.post("/usuarios/{usuario_id}/refeicoes/")
def criar_refeicao(usuario_id: int, refeicao: Refeicao):
  for usuario in usuarios:
    if usuario.id == usuario_id:
      if any(refeicao_atual.id == refeicao.id for refeicao_atual in usuario.refeicoes):
        raise HTTPException(status_code=400, detail="ID existente.")
      usuario.refeicoes.append(refeicao)
      return refeicao
  raise HTTPException(status_code="404", detail="Usuario não encontrado.")

# CRIAR UMA REFEICAO PARA UM USUARIO

@app.get("/usuarios/{usuario_id}/refeicoes/")
def listar_refeicoes(usuario_id: int):
  for usuario in usuarios:
    if usuario.id == usuario_id:
      return usuario.refeicoes
  raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Usuário não encontrado.")

# LISTAR A REFEICAO DE UM USUARIO

@app.get("/usuarios/{usuario_id}/refeicoes/{refeicao_id}")
def ler_refeicao(usuario_id: int, refeicao_id: int):
  for usuario in usuarios:
    if usuario.id == usuario_id:
      for refeicao in usuario.refeicoes:
        if refeicao.id == refeicao_id:
          return refeicao
      raise HTTPException(status_code=404, detail="Refeicao não encontrada.")  
  raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Usuário não encontrado.")  

# ATUALIZAR A REFEICAO DE UM USUARIO

@app.put("/usuarios/{usuario_id}/refeicoes/{refeicao_id}")
def atualizar_refeicao(usuario_id: int, refeicao_id: int, refeicao_att: Refeicao):
  for usuario in usuarios:
    if usuario.id == usuario_id:
      for i, refeicao in enumerate(usuario.refeicoes):
        if refeicao.id == refeicao_id:
          if refeicao_att.id != refeicao_id:
            refeicao_att.id = refeicao_id
          usuario.refeicoes[i] = refeicao_att
          return refeicao_att
      raise HTTPException(status_code=404, detail="Refeicao não encontrada.")
  raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Usuário não encontrado.")
    
# LISTAR TODOS OS ALIMENTOS

@app.get("/alimentos/")
def listar_usuarios() -> list[Alimento]:
  return alimentos

#endpoint to upload CSV file
@app.post("/carregar_csv/")
async def carregar_csv(file: UploadFile = File(...)):
  if file.filename.endswith(".csv"):
    contents = await file.read()

    with open(file.filename, 'wb') as f:
      f.write(contents)
    return {"msg": "Arquivo CSV carregado com sucesso."}
  else:
    return {"erro": "Apenas arquivos CSV são permitidos."}
  
#endpoint to read csv file and return as JSON
@app.get("/ler_csv/")
async def ler_csv(file_name: str):
  try:
    with open(file_name, 'r') as f:
      csv_reader = csv.DictReader(f)
      json_data = [row for row in csv_reader]
      return json_data
  except FileNotFoundError:
    return{"erro": "Arquivo não encontrado."}
  
#endpoint to write JSON data to CSV file
@app.post("escrever-csv/")
async def escrever_csv(data: CSV):
  with open(data.file_name, 'a', newline='') as f:
    fieldnames = ['nome', 'calorias', 'carboidratos', 'proteinas', 'acucar', 'sodio', 'gordura']
    writer = csv.DictWriter(f, fieldnames=fieldnames)

    if f.tell() == 0:
      writer.writeheader()
    for item in data.data:
      writer.writerow(item.dict())
  
  return{"msg": "Json data append to CSV file "}


#f4
@app.get("/contar-entidades/")
def contar_entidades(file_name: str):
  try:
    with open(file_name, 'r', newline='') as f:
      reader = csv.reader(f)
      next(reader)
      row_count = sum(1 for row in reader)
    return{"contagem": row_count}
  except FileNotFoundError:
    return {"erro": "Arquivo não encontrado."}

#f5
@app.get("/compactar-csv/")
def compactar_csv(file_name: str):
    zip_file = file_name.replace('.csv', '.zip')
    with zipfile.ZipFile(zip_file, 'w') as zip_ref:
        zip_ref.write(file_name)
    return {"zip_file": zip_file}

#f6
@app.get("/hash-sha256/")
def hash_sha256(file_name: str):
  sha256 = hashlib.sha256()
  with open(file_name, 'rb') as f:
    sha256.update(f.read())
    hash = sha256.hexdigest()
    return{"sha256": hash}


