from http import HTTPStatus
from fastapi import FastAPI, HTTPException
from models import Usuario, Refeicao, Alimento

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
  for usuario in usuarios:
    if usuario.id == usuario_id:
      return usuario
  raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Usuário não encontrado.")


@app.put("/usuarios/{usuario_id}")
def atualizar_usuario(usuario_id: int, usuario_att: Usuario) -> Usuario:
  for i, usuario in enumerate(usuarios):
    if usuario.id == usuario_id:
      if usuario_att.id != usuario_id:
        usuario_att.id = usuario_id
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


@app.post("/usuarios/{usuario_id}/refeicoes/")
def criar_refeicao(usuario_id: int, refeicao: Refeicao):
  for usuario in usuarios:
    if usuario.id == usuario_id:
      usuario.refeicoes.append(refeicao)
      return refeicao
    raise HTTPException(status_code="404", detail="Usuario não encontrado.")


@app.get("/usuarios/{usuario_id}/refeicoes/")
def listar_refeicoes(usuario_id: int):
  for usuario in usuarios:
    if usuario.id == usuario_id:
      return usuario.refeicoes


@app.get("/usuarios/{usuario_id}/refeicoes/{refeicao_id}")
def ler_refeicao(usuario_id: int, refeicao_id: int):
  for usuario in usuarios:
    if usuario.id == usuario_id:
      for refeicao in usuario.refeicoes:
        if refeicao.id == refeicao_id:
          return refeicao
  raise HTTPException(status_code=404, detail="Refeicao não encontrada.")    


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


