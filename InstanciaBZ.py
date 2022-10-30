# ************************************************
#   InstanciaBZ.py
#   Define a classe Instancia
#   Autor: Márcio Sarroglia Pinho
#       pinho@pucrs.br
# ************************************************

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Bezier import Bezier
from Ponto import *

""" Classe Instancia """
class InstanciaBZ:   
    def __init__(self):
        self.principal = False

        self.posicao = Ponto (0,0,0) 
        self.escala = Ponto (1,1,1)
        self.rotacao:float = 0.0
        self.modelo = None
        self.t = 0.0
        self.cor = (0,0,0)
        self.curva = None
        self.proxCurva = None
        self.proximas = None
        self.speed = 1

        self.jaEscolheu = False

        self.direcao = 1

        self.posCurva = 0
    
    """ Imprime os valores de cada eixo do ponto """
    # Faz a impressao usando sobrecarga de funcao
    # https://www.educative.io/edpresso/what-is-method-overloading-in-python
    def troca_a_proxima_curva(self, lado):
        if self.proxCurva is not None:
            self.posCurva += lado
            prox = self.proximas[self.posCurva % len(self.proximas)]
            if prox == self.proxCurva: self.troca_a_proxima_curva(lado)
            else: self.proxCurva = prox

    def setCurva(self, curva:Bezier):
        self.curva = curva

    def imprime(self, msg=None):
        if msg is not None:
            pass 
        else:
            print ("Rotacao:", self.rotacao)

    """ Define o modelo a ser usada para a desenhar """
    def setModelo(self, func):
        self.modelo = func

    def setPosicao(self, t):
        self.posicao = self.curva.Calcula(t)
        # print(self.posicao.x, self.posicao.y)

    def trocaCurva(self, nroCurva):
        self.nroCurva = nroCurva
        self.t = 0.0

    def Desenha(self):
        if self.principal:
            self.curva.Traca(color=(0,0,255))
            if self.proxCurva is not None:
                self.proxCurva[0].Traca(color=(0,255,0), lineWidth=4)
        
        #print ("Desenha")
        #self.escala.imprime("\tEscala: ")
        #print ("\tRotacao: ", self.rotacao)
        self.setPosicao(self.t)
        glPushMatrix()
        glColor3ub(self.cor[0], self.cor[1], self.cor[2])
        glTranslatef(self.posicao.x, self.posicao.y, 0)
        glRotatef(self.rotacao, 0, 0, 1)
        glScalef(self.escala.x, self.escala.y, self.escala.z)
        self.modelo()
        glPopMatrix()

    
