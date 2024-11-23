from http import HTTPStatus
from fastapi import FastAPI, HTTPException
from models import Usuario

app = FastAPI()

usuarios: list[Usuario] = []

@app.get("/")
def padrao(): 
  return {"msg": "Bem vindo ao Sistema de Gestão Nutricional."}


@app.post("/usuarios/")
def criar_usuario(usuario: Usuario) -> Usuario:
  if any(usuario_atual.id == usuario.id for usuario_atual in usuarios):
    raise HTTPException(status_code=400, detail="ID existente.")
  usuarios.append(usuario)
  return usuario


@app.get("/usuarios/")
def listar_usuarios() -> list[Usuario]:
  return usuarios

@app.get("/usuarios/{usuario_id}")
def ler_usuario(usuario_id: int) -> Usuario:
  for usuario in enumerate(usuarios):
    if usuario.id == usuario_id:
      return usuario
  raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Usuário não encontrado.")


@app.put("/usuarios/{usuario_id}")
def atualizar_usuario(usuario_id: int, usuario_att: Usuario) -> Usuario:
  for i, usuario in enumerate(usuarios):
    if usuario.id == usuario_id:
      if usuario_att.id != usuario_id:
        usuario_att.id == usuario_id
      usuarios[i] = usuario_att
      return usuario_att
  raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Usuário não encontrado.")
  

@app.delete("/usuarios/{usuario_id}")
def remover_item(usuario_id: int):
    for usuario in usuarios:
        if usuario.id == usuario_id:
            usuarios.remove(usuario)
            return {"msg": "Usuário removido."}
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Usuário não encontrado.")