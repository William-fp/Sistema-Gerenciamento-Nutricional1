import os
import shutil
from http import HTTPStatus
from fastapi import FastAPI, HTTPException, UploadFile, File
from models import Usuario, Refeicao, Alimento
import pandas as pd
import uuid
import csv
import os
import io
from pydantic import BaseModel
import zipfile
import hashlib

app = FastAPI()

usuarios: list[Usuario] = []
alimentos: list[Alimento] = []

if not os.path.exists('./csv'):
  os.makedirs('csv')

class CSV(BaseModel):
  data: list[Alimento]
  file_name: str


@app.get("/")
def padrao(): 
  return {"msg": "Bem vindo ao Sistema de Gestão Nutricional."}

# CRIAR USUARIO

@app.post("/usuarios/")
def criar_usuario(usuario: Usuario) -> Usuario:
  usuario_uuid = uuid.uuid4()
  data = pd.DataFrame([usuario.dict()])
  data.to_csv(f"./csv/usuario_{usuario_uuid}.csv", index=False)
  os.makedirs(f'./csv/usuario_refeicao_{usuario_uuid}')
  return usuario

# LISTAR TODOS OS USUARIOS

@app.get("/usuarios/")
def listar_usuarios() -> list[dict]:
  usuarios = []
  for arquivo in os.listdir("./csv"):
      print(f"Lendo arquivo {arquivo}")
      if arquivo.startswith("usuario_") and arquivo.endswith(".csv"):
          usuario_id = arquivo.replace("usuario_", "").replace(".csv", "")
          df = pd.read_csv(os.path.join("./csv", arquivo))
          for _, row in df.iterrows():
              usuario = row.to_dict()
              usuario['id'] = usuario_id
              usuarios.append(usuario)
  return usuarios

# LISTAR UM USUARIO ESPECIFICO

@app.get("/usuarios/{usuario_id}")
def ler_usuario(usuario_id) -> dict:
  arquivo = f"usuario_{usuario_id}.csv"
  if not os.path.exists(os.path.join("./csv", arquivo)):
        return {"error": "Usuário não existe."}
  else:
      df = pd.read_csv(os.path.join("./csv", arquivo))
      usuario = df.iloc[0].to_dict()
      usuario['id'] = usuario_id
      return usuario
  
  
# ATUALIZAR UM USUARIO

@app.put("/usuarios/{usuario_id}")
def atualizar_usuario(usuario_id: str, usuario: Usuario) -> Usuario:
    diretorio = f"./csv/usuario_{usuario_id}.csv"
    
    if not os.path.exists(diretorio):
      return {"error": "Usuário não existe."}    
    df = pd.read_csv(diretorio)
    
    df.loc[0, 'nome'] = usuario.nome
    df.loc[0, 'altura'] = usuario.altura
    df.loc[0, 'idade'] = usuario.idade
    df.loc[0, 'peso'] = usuario.peso

    df.to_csv(diretorio, index=False)
    
    return usuario
  
# DELETAR UM USUARIO

@app.delete("/usuarios/{usuario_id}")
def remover_usuario(usuario_id):
  refeicoes_diretorio = f"usuario_refeicao_{usuario_id}"
  arquivo = f"usuario_{usuario_id}.csv"
  if not os.path.exists(os.path.join("./csv", arquivo)):
        return {"error": "Usuário não existe."}
  else:
      os.remove(os.path.join("./csv", arquivo))
      shutil.rmtree(os.path.join("./csv/", refeicoes_diretorio))
      return {"message": f"Usuário {usuario_id} deletado com sucesso!"}  

# CRIAR UMA REFEICAO PARA UM USUARIO

@app.post("/refeicoes/")
def criar_refeicao(dados: dict[str, object]) -> Refeicao:
  refeicao_id = uuid.uuid4()
  usuario_id = dados.get("usuario_id")
  refeicao = dados.get("refeicao")
  data = pd.DataFrame([refeicao])
  data.to_csv(f"./csv/usuario_refeicao_{usuario_id}/{refeicao_id}.csv", index=False)
  return refeicao

# LISTAR AS REFEICOES DE UM USUARIO

@app.get("/refeicoes/{usuario_id}")
def listar_refeicoes(usuario_id: str):
    caminho_pasta = f"./csv/usuario_refeicao_{usuario_id}"

    if os.path.isdir(caminho_pasta):
        arquivos = os.listdir(caminho_pasta)

        if arquivos: 
            refeicoes = [] 

            for arquivo in arquivos:
                caminho_arquivo = os.path.join(caminho_pasta, arquivo)
                try:
                    refeicao = pd.read_csv(caminho_arquivo).to_dict(orient="records")
                except Exception as e:
                    with open(caminho_arquivo, "r") as f:
                        refeicao = f.read()
                id_refeicao = arquivo.replace(".csv", "")
                refeicoes.append({
                    "id": id_refeicao,
                    "refeicao": refeicao
                })

            return {"refeicoes": refeicoes}
        else:
            return {"msg": "Nenhuma refeição encontrada."}
    else:
        return {"error": f"Erro ao acessar diretório do usuario de id {usuario_id}"}

# ATUALIZAR A REFEICAO DE UM USUARIO

@app.put("/refeicoes/{usuario_id}/{refeicao_id}")
def atualizar_refeicao(usuario_id: str, refeicao_id : str, refeicao : Refeicao):

    diretorio = f"./csv/usuario_refeicao_{usuario_id}/{refeicao_id}.csv"
    
    if not os.path.exists(diretorio):
      return {"error": "Refeição não existe."}   
     
    df = pd.read_csv(diretorio)
    
    df.loc[0, 'tipo'] = refeicao.tipo
    df.loc[0, 'alimentos'] = refeicao.alimentos

    df.to_csv(diretorio, index=False)

    return {"msg": f"Refeição {refeicao_id} do usuário {usuario_id} atualizada com sucesso!", "nova_refeicao": refeicao}

@app.put("/refeicoes/{usuario_id}")
def atualizar_usuario(usuario_id: str, usuario: Usuario) -> Usuario:
    diretorio = f"./csv/usuario_{usuario_id}.csv"
    
    if not os.path.exists(diretorio):
      return {"error": "Usuário não existe."}    
    df = pd.read_csv(diretorio)
    
    df.loc[0, 'nome'] = usuario.nome
    df.loc[0, 'altura'] = usuario.altura
    df.loc[0, 'idade'] = usuario.idade
    df.loc[0, 'peso'] = usuario.peso

    df.to_csv(diretorio, index=False)
    
    return usuario


# REMOVER REFEICAO

@app.delete("/refeicoes/")
def remover_refeicao(dados: dict[str, str]):
  usuario_id = dados.get("usuario_id")
  refeicao_id = dados.get("refeicao_id")
  if os.path.exists(f'./csv/usuario_refeicao_{usuario_id}'):
    os.remove(os.path.join(f"./csv/usuario_refeicao_{usuario_id}/", refeicao_id))
    return {"msg": "Refeição removida."}
  else:
    return {"error": "Usuário não existe."}

# LISTAR TODOS OS ALIMENTOS

@app.get("/alimentos/")
def listar_alimentos() -> list[dict]:
    alimentos = []
    for arquivo in os.listdir("./csv"):
        if arquivo.startswith("alimento_") and arquivo.endswith(".csv"):

            alimento_id = arquivo.replace("alimento_", "").replace(".csv", "")

            df = pd.read_csv(os.path.join("./csv", arquivo))
            for _, row in df.iterrows():
                alimento = row.to_dict()
                alimento['id'] = alimento_id
                alimentos.append(alimento)

    return alimentos

# CRIAR UM ALIMENTO

@app.post("/alimentos/")
def criar_alimento(alimento: Alimento) -> Alimento:
  data = pd.DataFrame([alimento.dict()])
  alimento_uuid = uuid.uuid4()
  data.to_csv(f"./csv/alimento_{alimento_uuid}.csv", index=False)
  return alimento
  

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

