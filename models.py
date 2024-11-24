from pydantic import BaseModel

class Alimento(BaseModel):
  nome: str
  calorias: float
  carboidratos: float 
  proteinas: float 
  acucar: float 
  sodio: float 
  gordura: float 


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