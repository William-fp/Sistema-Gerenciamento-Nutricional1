from http import HTTPStatus
from fastapi import FastAPI, HTTPException
from models import Usuario, Refeicao, Alimento

app = FastAPI()

usuarios: list[Usuario] = []
alimentos: list[Alimento] = []


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
def remover_item(usuario_id: int):
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
      usuario.refeicoes.append(refeicao)
      return refeicao
    raise HTTPException(status_code="404", detail="Usuario não encontrado.")

# CRIAR UMA REFEICAO PARA UM USUARIO

@app.get("/usuarios/{usuario_id}/refeicoes/")
def listar_refeicoes(usuario_id: int):
  for usuario in usuarios:
    if usuario.id == usuario_id:
      return usuario.refeicoes

# LISTAR A REFEICAO DE UM USUARIO

@app.get("/usuarios/{usuario_id}/refeicoes/{refeicao_id}")
def ler_refeicao(usuario_id: int, refeicao_id: int):
  for usuario in usuarios:
    if usuario.id == usuario_id:
      for refeicao in usuario.refeicoes:
        if refeicao.id == refeicao_id:
          return refeicao
  raise HTTPException(status_code=404, detail="Refeicao não encontrada.")    

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
    
# LISTAR TODOS OS ALIMENTOS

@app.get("/alimentos/")
def listar_usuarios() -> list[Alimento]:
  return alimentos