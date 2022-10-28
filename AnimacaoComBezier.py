# ***********************************************************************************
#   ExibePoligonos.py
#       Autor: Márcio Sarroglia Pinho
#       pinho@pucrs.br
#   Este programa cria um conjunto de INSTANCIAS
#   Para construir este programa, foi utilizada a biblioteca PyOpenGL, disponível em
#   http://pyopengl.sourceforge.net/documentation/index.html
#
#   Sugere-se consultar também as páginas listadas
#   a seguir:
#   http://bazaar.launchpad.net/~mcfletch/pyopengl-demo/trunk/view/head:/PyOpenGL-Demo/NeHe/lesson1.py
#   http://pyopengl.sourceforge.net/documentation/manual-3.0/index.html#GLUT
#
#   No caso de usar no MacOS, pode ser necessário alterar o arquivo ctypesloader.py,
#   conforme a descrição que está nestes links:
#   https://stackoverflow.com/questions/63475461/unable-to-import-opengl-gl-in-python-on-macos
#   https://stackoverflow.com/questions/6819661/python-location-on-mac-osx
#   Veja o arquivo Patch.rtf, armazenado na mesma pasta deste fonte.
# ***********************************************************************************
import math

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Poligonos import *
from InstanciaBZ import *
from Bezier import *

from random import randint
# ***********************************************************************************

cores = {
    0: (188,143,143),
    1: (28,28,28),
    2: (70,130,180),
    3: (0,255,127),
    4: (218,165,32),
    5: (123,104,238),
    6: (75,0,130),
    7: (255,0,255),
    8: (210,105,30),
    9: (220,20,60),
    10: (255,0,0),
    11: (255,255,0),
    12: (0,0,0),
}

t = 0

# Modelos de Objetos
MeiaSeta = Polygon()
Mastro = Polygon()

# Limites da Janela de Seleção
Min = Ponto()
Max = Ponto()

# lista de instancias do Personagens
Personagens = [] 

listaDeCurvas = []
listaDePontos = []

proximas_e_anteriores = {}

# ***********************************************************************************
# Lista de curvas Bezier

angulo = 0.0

def carregaPontos():
    global listaDeCurvas, listaDePontos
    for line in open('Pontos.txt'):
        x, y = (int(val) for val in line.split())
        listaDePontos.append(Ponto(x,y))
    pid = 0
    for line in open('Curvas.txt'):
        p1, p2, p3 = [listaDePontos[int(i)] for i in line.split()]
        bezier = Bezier(p1, p2, p3, pid=pid)
        pid+=1
        listaDeCurvas.append(bezier)
        proximas_e_anteriores[bezier.id] = {
            'curva': bezier,
            'proximas': [],
            'anteriores': []
        }

    for i in range(len(listaDeCurvas)):
        for j in range(len(listaDeCurvas)):
            atual:Bezier = listaDeCurvas[i]
            outra:Bezier = listaDeCurvas[j]
            if atual.p3 == outra.p1:
                proximas_e_anteriores[atual.id]['proximas'].append((outra, 1))
            elif atual.p3 == outra.p3 and atual != outra:
                proximas_e_anteriores[atual.id]['proximas'].append((outra, -1))
            
            if atual.p1 == outra.p3:
                proximas_e_anteriores[atual.id]['anteriores'].append((outra, 1))
            elif atual.p1 == outra.p1 and atual != outra:
                proximas_e_anteriores[atual.id]['anteriores'].append((outra, -1)) 
    
    for bezier in listaDeCurvas:
        print(f'Bezier {str(bezier)}:')
        proximas = proximas_e_anteriores[bezier.id]['proximas']
        anteriores = proximas_e_anteriores[bezier.id]['anteriores']


def DesenhaLinha (P1, P2):
    glBegin(GL_LINES)
    glVertex3f(P1.x,P1.y,P1.z)
    glVertex3f(P2.x,P2.y,P2.z)
    glEnd()

# ****************************************************************
def RotacionaAoRedorDeUmPonto(alfa: float, P: Ponto):
    glTranslatef(P.x, P.y, P.z)
    glRotatef(alfa, 0,0,1)
    glTranslatef(-P.x, -P.y, -P.z)

# ***********************************************************************************
def reshape(w,h):

    global Min, Max
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Cria uma folga na Janela de Selecão, com 10% das dimensoes do poligono
    BordaX = abs(Max.x-Min.x)*0.1
    BordaY = abs(Max.y-Min.y)*0.1
    asp = w/h
    #glOrtho(Min.x-BordaX, Max.x+BordaX, Min.y-BordaY, Max.y+BordaY, 0.0, 1.0)
    glOrtho(Min.x*asp, Max.x*asp, Min.y, Max.y, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

# ***********************************************************************************
def DesenhaMastro():
    Mastro.desenhaPoligono()

# ***********************************************************************************
def DesenhaSeta():
    glPushMatrix()
    MeiaSeta.desenhaPoligono()
    glScaled(1,-1, 1)
    MeiaSeta.desenhaPoligono()
    glPopMatrix()

# ***********************************************************************************
def DesenhaApontador():
    glPushMatrix()
    glTranslated(-4, 0, 0)
    DesenhaSeta()
    glPopMatrix()
# **********************************************************************
def DesenhaHelice():
    glPushMatrix()
    for i in range (4):   
        glRotatef(90, 0, 0, 1)
        DesenhaApontador()
    glPopMatrix()

def DesenhaHelicesGirando():
    global angulo
    #print ("angulo:", angulo)
    glPushMatrix()
    glRotatef(angulo, 0, 0, 1)
    DesenhaHelice()
    glPopMatrix()

def DesenhaCatavento():
    glLineWidth(3)
    glPushMatrix()
    DesenhaMastro()
    glPushMatrix()
    glColor3f(1,0,0)
    glTranslated(0,3,0)
    glScaled(0.2, 0.2, 1)
    DesenhaHelicesGirando()
    glPopMatrix()
    glPopMatrix()

def desenhaSeta():
    glLineWidth(3)
    glPushMatrix()
    glColor3f(0,0,0)
    DesenhaSeta()
    glPopMatrix()

# **************************************************************
def DesenhaEixos():
    global Min, Max

    Meio = Ponto(); 
    Meio.x = (Max.x+Min.x)/2
    Meio.y = (Max.y+Min.y)/2
    Meio.z = (Max.z+Min.z)/2

    glBegin(GL_LINES)
    #  eixo horizontal
    glVertex2f(Min.x,Meio.y)
    glVertex2f(Max.x,Meio.y)
    #  eixo vertical
    glVertex2f(Meio.x,Min.y)
    glVertex2f(Meio.x,Max.y)
    glEnd()

# ***********************************************************************************
def DesenhaPersonagens():
    for I in Personagens:
        I.Desenha()

# ***********************************************************************************
def DesenhaCurvas():
    global cores
    contador = 0
    for I in listaDeCurvas:
        r, g, b = cores[contador%12]
        glColor3ub(r,g,b)
        I.Traca()
        contador+=1

# ***********************************************************************************
def display():

	# Limpa a tela coma cor de fundo
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glLineWidth(2)

    DesenhaPersonagens()
    DesenhaCurvas()
    
    glutSwapBuffers()

# ***********************************************************************************
# The function called whenever a key is pressed. 
# Note the use of Python tuples to pass in: (key, x, y)
#ESCAPE = '\033'
ESCAPE = b'\x1b'
def keyboard(*args):
    print (args)
    # If escape is pressed, kill everything.
    if args[0] == b'q':
        os._exit(0)
    if args[0] == ESCAPE:
        os._exit(0)
# Forca o redesenho da tela
    glutPostRedisplay()

# **********************************************************************
#  arrow_keys ( a_keys: int, x: int, y: int )   
# **********************************************************************
def mover(p:InstanciaBZ, direcao):
    inicial = p.posicao
    p.rotacao = 0
    p.t += p.direcao * 0.05 * direcao
    if p.t >= 1 or p.t <= 0:
        if p.t > 0.5:
            print('PROXIMA')
            proximas = proximas_e_anteriores[p.curva.id]['proximas']
            prox, direcao = proximas[randint(0, len(proximas)-1)]
            p.curva = prox
            p.direcao = direcao
            p.t = 0 if direcao > 0 else 1
        else:
            print("ANTERIOR")
            anteriores = proximas_e_anteriores[p.curva.id]['anteriores']
            for val in anteriores:
                print(val[0])
            prox, direcao = anteriores[randint(0, len(anteriores)-1)]
            p.curva = prox
            p.direcao = -direcao
            p.t = 1 if direcao > 0 else 0
    p.setPosicao(p.t)
    final = p.posicao
    variacao = final - inicial
    delta = variacao.y / variacao.x

    p.rotacao = math.atan2(variacao.y, variacao.x) * 180 / math.pi
    # p.rotacao += 180 if p.direcao < 0 else 0
    # print(delta)



def arrow_keys(a_keys: int, x: int, y: int):
    global Personagens

    if a_keys == GLUT_KEY_UP:         # Se pressionar UP
        mover(Personagens[0], 1)

    if a_keys == GLUT_KEY_DOWN:       # Se pressionar DOWN
        mover(Personagens[0], -1)
    if a_keys == GLUT_KEY_LEFT:       # Se pressionar LEFT
        Personagens[0].posicao.x -= 1
        pass
    if a_keys == GLUT_KEY_RIGHT:      # Se pressionar RIGHT
        Personagens[0].posicao.x += 1
        pass

    glutPostRedisplay()

# ***********************************************************************************
#
# ***********************************************************************************
def mouse(button: int, state: int, x: int, y: int):
    global PontoClicado
    if (state != GLUT_DOWN): 
        return
    if (button != GLUT_RIGHT_BUTTON):
        return
    #print ("Mouse:", x, ",", y)
    # Converte a coordenada de tela para o sistema de coordenadas do 
    # Personagens definido pela glOrtho
    vport = glGetIntegerv(GL_VIEWPORT)
    mvmatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
    projmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
    realY = vport[3] - y
    worldCoordinate1 = gluUnProject(x, realY, 0, mvmatrix, projmatrix, vport)

    PontoClicado = Ponto (worldCoordinate1[0],worldCoordinate1[1], worldCoordinate1[2])
    PontoClicado.imprime("Ponto Clicado:")

    glutPostRedisplay()

# ***********************************************************************************
#
# ***********************************************************************************
def mouseMove(x: int, y: int):
    #glutPostRedisplay()
    return

def CarregaModelos():
    global MeiaSeta, Mastro
    MeiaSeta.LePontosDeArquivo("MeiaSeta.txt")
    # Mastro.LePontosDeArquivo("Mastro.txt")

# ***********************************************************************************
# Esta função deve instanciar todos os personagens do cenário
# ***********************************************************************************
def CriaInstancias():
    global Personagens
    Personagens.append(InstanciaBZ())
    Personagens[0].modelo = DesenhaSeta
    Personagens[0].escala = Ponto (.25,.25,.25) 
    Personagens[0].cor = (255,255,255)
    Personagens[0].rotacao = 0
    Personagens[0].posicao = Ponto(0,0)
    Personagens[0].setCurva(listaDeCurvas[0])

    # Personagens.append(InstanciaBZ())
    # Personagens[1].posicao = Ponto(3,0)
    # Personagens[1].modelo = DesenhaCatavento
    # Personagens[1].rotacao = -90
  
    # Personagens.append(InstanciaBZ())
    # Personagens[2].posicao = Ponto(0,-5)
    # Personagens[2].modelo = DesenhaCatavento
    # Personagens[2].rotacao = 0

# ***********************************************************************************
def init():
    global Min, Max
    # Define a cor do fundo da tela (AZUL)
    glClearColor(0, 0, 0, 1)
    # CriaCurvas()
    carregaPontos()
    CarregaModelos()
    CriaInstancias()

    zoom:float = 5
    Min = Ponto(-zoom,-zoom)
    Max = Ponto(zoom,zoom)

def animate():
    global angulo, Personagens
    # personagem:InstanciaBZ = Personagens[0]
    # personagem.setPosicao(personagem.t)
    # print(personagem.t)
    # personagem.t += 0.001
    # personagem.t %= 1
    # angulo = angulo + .1
    glutPostRedisplay()

# ***********************************************************************************
# Programa Principal
# ***********************************************************************************


glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA)
# Define o tamanho inicial da janela grafica do programa
glutInitWindowSize(750, 750)
glutInitWindowPosition(100, 100)
wind = glutCreateWindow("Exemplo de Criacao de Instancias")
glutDisplayFunc(display)
glutIdleFunc(animate)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutSpecialFunc(arrow_keys)
glutMouseFunc(mouse)
init()

try:
    glutMainLoop()
except SystemExit:
    pass
