from pydantic import BaseModel

class Alimento(BaseModel):
  nome: str
  calorias: float = 0
  carboidratos: float = 0
  proteinas: float = 0
  acucar: float = 0
  sodio: float = 0
  gordura: float = 0

class Refeicao(BaseModel):
  tipo: str            #almoço,janta...
  alimentos: list[str]


class Usuario(BaseModel):
  nome: str
  altura: float
  idade: int
  peso: float