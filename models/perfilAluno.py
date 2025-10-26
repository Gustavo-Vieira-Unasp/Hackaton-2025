from models.perfil import Perfil
import os
import system

class perfilAluno():
    def __innit__(self, value):
        self.ra: aluno = value
        self.idade: int = None
        self.sexo: str = None
        self.curso: str = None
        self.Religião: str = None
        self.interesse: list = []
        