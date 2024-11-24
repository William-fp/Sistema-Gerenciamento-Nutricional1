from fastapi.responses import FileResponse
import os
import shutil
from http import HTTPStatus
from fastapi import FastAPI, HTTPException, UploadFile, File
from models import Usuario, Refeicao, Alimento
import pandas as pd
import uuid
import csv
import os
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
  usuario_data = usuario.dict()
  usuario_data['usuario_id'] = usuario_uuid

  if os.path.exists('./csv/usuarios.csv'):
    usuarios_df = pd.read_csv('./csv/usuarios.csv')
    new_user_df = pd.DataFrame([usuario_data])
    usuarios_df = pd.concat([usuarios_df, new_user_df], ignore_index=True)
    usuarios_df.to_csv('./csv/usuarios.csv', index=False)
  else:
    usuarios_df = pd.DataFrame([usuario_data])
    usuarios_df.to_csv('./csv/usuarios.csv', index=False)

  os.makedirs(f'./csv/usuario_refeicao_{usuario_uuid}', exist_ok=True)

  return usuario

# LISTAR TODOS OS USUARIOS

@app.get("/usuarios/")
def listar_usuarios():
  if os.path.exists('./csv/usuarios.csv'):
      usuarios_df = pd.read_csv('./csv/usuarios.csv')
      usuarios_list = usuarios_df.to_dict(orient='records')
      return {"usuarios": usuarios_list}
  else:
      raise HTTPException(status_code=404, detail="Nenhum usuário encontrado.")

# LISTAR UM USUARIO ESPECIFICO

@app.get("/usuarios/{usuario_id}")
def listar_usuario(usuario_id: str):
  if os.path.exists('./csv/usuarios.csv'):
    usuarios_df = pd.read_csv('./csv/usuarios.csv')
    usuario = usuarios_df[usuarios_df['usuario_id'] == usuario_id]
    
    if not usuario.empty:
        return {"usuario": usuario.to_dict(orient='records')[0]}
    else:
        raise HTTPException(status_code=404, detail=f"Usuário com id {usuario_id} não encontrado.")
  
  
# ATUALIZAR UM USUARIO

@app.put("/usuarios/{usuario_id}")
def atualizar_usuario(usuario_id: str, usuario: Usuario):
  if os.path.exists('./csv/usuarios.csv'):
    usuarios_df = pd.read_csv('./csv/usuarios.csv')
    
    usuario_idx = usuarios_df[usuarios_df['usuario_id'] == usuario_id].index
    
    if usuario_idx.empty:
        raise HTTPException(status_code=404, detail=f"usuario de  id {usuario_id} não existe.")
    
    usuarios_df.loc[usuario_idx, 'nome'] = usuario.nome
    usuarios_df.loc[usuario_idx, 'altura'] = usuario.altura
    usuarios_df.loc[usuario_idx, 'idade'] = usuario.idade
    usuarios_df.loc[usuario_idx, 'peso'] = usuario.peso

    usuarios_df.to_csv('./csv/usuarios.csv', index=False)
    
    return {"msg": f"usuario de id {usuario_id} atualizado"}

  
# DELETAR UM USUARIO

@app.delete("/usuarios/{usuario_id}")
def deletar_usuario(usuario_id: str):
  if os.path.exists('./csv/usuarios.csv'):
      usuarios_df = pd.read_csv('./csv/usuarios.csv')
      
      usuario = usuarios_df[usuarios_df['usuario_id'] == usuario_id]
      
      if not usuario.empty:
          usuarios_df = usuarios_df[usuarios_df['usuario_id'] != usuario_id]
          
          usuarios_df.to_csv('./csv/usuarios.csv', index=False)

          return {"msg": f"Usuário com id {usuario_id} removido com sucesso."}
      else:
          raise HTTPException(status_code=404, detail=f"Usuário com id {usuario_id} não encontrado.")
  else:
      raise HTTPException(status_code=404, detail="Arquivo de usuários não encontrado.")

# CRIAR UMA REFEICAO PARA UM USUARIO

@app.post("/refeicoes/")
def criar_refeicao(dados: dict[str, object]):
    usuario_id = dados.get("usuario_id")
    refeicao = dados.get("refeicao")
    refeicao_id = uuid.uuid4()
    refeicao['refeicao_id'] = str(refeicao_id)
    refeicao['usuario_id'] = usuario_id
    
    if not usuario_id or not refeicao:
        raise HTTPException(status_code=400, detail="usuario_id e refeicao são obrigatórios")
    
    df = pd.DataFrame([refeicao])
    arquivo_csv = f'./csv/refeicoes_usuario_{usuario_id}.csv'
    if os.path.exists(arquivo_csv):
        df.to_csv(arquivo_csv, mode='a', header=False, index=False)
    else:
        df.to_csv(arquivo_csv, mode='w', header=True, index=False)
    
    return {"msg": f"refeição adicionada ao usuario {usuario_id}", "refeicao_id": str(refeicao_id)}

# LISTAR AS REFEICOES DE UM USUARIO

@app.get("/refeicoes/{usuario_id}")
def listar_refeicoes(usuario_id: str):
    arquivo_csv = f'./csv/refeicoes_usuario_{usuario_id}.csv'
    
    if not os.path.exists(arquivo_csv):
        raise HTTPException(status_code=404, detail="Usuário não encontrado ou ainda não tem refeições registradas.")
    
    df = pd.read_csv(arquivo_csv)
    if df.empty:
        raise HTTPException(status_code=404, detail="Nenhuma refeição encontrada para o usuário.")
    
    refeicoes = df.to_dict(orient="records")
    return {"usuario_id": usuario_id, "refeicoes": refeicoes}

# ATUALIZAR A REFEICAO DE UM USUARIO

@app.put("/refeicoes/{usuario_id}/{refeicao_id}")
def atualizar_refeicao(usuario_id: str, refeicao_id: str, dados: dict):
    # Caminho do arquivo CSV do usuário
    arquivo_csv = f'./csv/refeicoes_usuario_{usuario_id}.csv'
    
    # Verificar se o arquivo existe
    if not os.path.exists(arquivo_csv):
        raise HTTPException(status_code=404, detail="Usuário não encontrado ou ainda não tem refeições registradas.")
    
    df = pd.read_csv(arquivo_csv)
    
    if df.empty:
        raise HTTPException(status_code=404, detail="Nenhuma refeição encontrada para o usuário.")
    
    refeicao_index = df[df['refeicao_id'] == refeicao_id].index
    
    if len(refeicao_index) == 0:
        raise HTTPException(status_code=404, detail="Refeição não encontrada.")
    
    for key, value in dados.items():
        if key in df.columns:
            df.at[refeicao_index[0], key] = value
    
    df.to_csv(arquivo_csv, index=False)
    
    return {"msg": "Refeição atualizada com sucesso."}

# REMOVER REFEICAO

@app.delete("/refeicoes/{usuario_id}/{refeicao_id}")
def remover_refeicao(usuario_id: str, refeicao_id: str):
    arquivo_csv = f'./csv/refeicoes_usuario_{usuario_id}.csv'
    if not os.path.exists(arquivo_csv):
        raise HTTPException(status_code=404, detail="Usuário não encontrado ou ainda não tem refeições registradas.")
    
    df = pd.read_csv(arquivo_csv)
    if df.empty:
        raise HTTPException(status_code=404, detail="Nenhuma refeição encontrada para o usuário.")
    refeicao_index = df[df['refeicao_id'] == refeicao_id].index
    if len(refeicao_index) == 0:
        raise HTTPException(status_code=404, detail="Refeição não encontrada.")
    
    df = df.drop(refeicao_index)
    df.to_csv(arquivo_csv, index=False)
    
    return {"msg": "Refeição removida com sucesso."}

# LISTAR TODOS OS ALIMENTOS

@app.get("/alimentos/")
def listar_alimentos():
    df = pd.read_csv('./csv/alimentos.csv')
    alimentos = df.to_dict(orient="records")
    return {"alimentos": alimentos}
  
# FAZER UPLOAD DE CSV
@app.post("/carregar_csv/")
async def carregar_csv(file: UploadFile = File(...)):
  if file.filename.endswith(".csv"):
    contents = await file.read()

    with open(file.filename, 'wb') as f:
      f.write(contents)
    return {"msg": "Arquivo CSV carregado com sucesso."}
  else:
    return {"erro": "Apenas arquivos CSV são permitidos."}
  
# CONTAR ENTIDADES

@app.get("/contar-entidades/{file_name}")
def contar_entidades(file_name: str):
  try:
    with open(os.path.join("./csv/", file_name), 'r', newline='') as f:
      reader = csv.reader(f)
      next(reader)
      row_count = sum(1 for row in reader)
    return{"contagem": row_count}
  except FileNotFoundError:
    return {"erro": "Arquivo não encontrado."}

# COMPACTAR CSV

@app.get("/compactar-csv/{file_name}")
def compactar_csv(file_name: str):
    file_name = os.path.join("./csv", file_name)
    zip_file = file_name.replace('.csv', '.zip')
    with zipfile.ZipFile(zip_file, 'w') as zip_ref:
        zip_ref.write(file_name)
    return FileResponse(zip_file, media_type='application/zip', filename=zip_file)

# HASHEAR EM SHA256

@app.get("/hash-sha256/{file_name}")
def hash_sha256(file_name: str):
  sha256 = hashlib.sha256()
  with open(os.path.join("./csv/", file_name) , 'rb') as f:
    sha256.update(f.read())
    hash = sha256.hexdigest()
    return{"sha256": hash}