from pydantic import BaseModel

class Alimento(BaseModel):
  nome: str
  quantidade: float
  unidade: str          #grama, kilo


class Refeicao(BaseModel):
  id: int
  tipo: str            #almoço,janta...
  alimentos: list[Alimento] = []


class Usuario(BaseModel):
  id: int
  nome: str
  altura: float
  idade: int
  peso: float
  refeicoes: list[Refeicao] = []