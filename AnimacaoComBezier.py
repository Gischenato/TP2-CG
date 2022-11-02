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
    1: (89,120,33),
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

colidiu = False
SPEED = 1

# Modelos de Objetos
MeiaSeta = Polygon()
Mastro = Polygon()
MeiaSetaInimiga = Polygon()

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


def carregaPontos():
    global listaDeCurvas, listaDePontos
    for line in open('SuperPontos.txt'):
        x, y = (int(val) for val in line.split())
        listaDePontos.append(Ponto(x,y))
    pid = 0
    for line in open('SuperCurvas.txt'):
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
    
    # for bezier in listaDeCurvas:
    #     print(f'Bezier {str(bezier)}:')
    #     proximas = proximas_e_anteriores[bezier.id]['proximas']
    #     anteriores = proximas_e_anteriores[bezier.id]['anteriores']


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

def DesenhaSetaInimiga():
    glPushMatrix()
    MeiaSetaInimiga.desenhaPoligono()
    glScaled(1,-1, 1)
    MeiaSetaInimiga.desenhaPoligono()
    glPopMatrix()

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
        # r, g, b = cores[contador%12]
        r, g, b = (255,0,0)
        glColor3ub(r,g,b)
        I.Traca()
        contador+=1


# ***********************************************************************************
def display():
    global colidiu
	# Limpa a tela coma cor de fundo
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glLineWidth(2)
    colidiu = checaColisao(Personagens[0])


    DesenhaCurvas()
    DesenhaPersonagens()
    
    glutSwapBuffers()

# ***********************************************************************************
# The function called whenever a key is pressed. 
# Note the use of Python tuples to pass in: (key, x, y)
#ESCAPE = '\033'
ESCAPE = b'\x1b'
def keyboard(*args):
    global Personagens, SPEED
    print (args)
    # If escape is pressed, kill everything.
    if args[0] == b'q':
        os._exit(0)
    if args[0] == b'r':
        init()
    if args[0] == b' ':
        Personagens[0].speed = 0 if Personagens[0].speed == SPEED else SPEED
    if args[0] == ESCAPE:
        os._exit(0)
# Forca o redesenho da tela
    glutPostRedisplay()

# **********************************************************************
#  arrow_keys ( a_keys: int, x: int, y: int )   
# **********************************************************************
def proxima_curva(p:InstanciaBZ):
    global proximas_e_anteriores
    if p.t > 0.5:
        proximas = proximas_e_anteriores[p.curva.id]['proximas']
        proxima = proximas[randint(0, len(proximas)-1)]
        p.proximas = proximas
        p.proxCurva = proxima
    else:
        anteriores = proximas_e_anteriores[p.curva.id]['anteriores']
        anterior = anteriores[randint(0, len(anteriores)-1)]
        p.proximas = anteriores
        p.proxCurva = anterior
    p.jaEscolheu = True

def mover(p:InstanciaBZ):
    if p.speed == 0: return
    inicial = p.posicao
    p.rotacao = 0
    deltaT = p.speed/p.curva.tamanho*.8
    p.t = p.t + p.direcao * deltaT

    if p.direcao == 1 and p.t >= .5 or p.direcao == -1 and p.t <= .5:
        if not p.jaEscolheu:
            proxima_curva(p)
            if p.principal: print('Proxima curva: ', p.proxCurva[0].id)
    else:
        p.proxCurva = None
        p.jaEscolheu = False


    if p.t >= 1 or p.t <= 0:
        prox, direcao = p.proxCurva
        p.curva = prox
        if p.t > 0.5:
            p.t = 0 if direcao > 0 else 1
            p.direcao = direcao
        else:
            p.t = 1 if direcao > 0 else 0
            p.direcao = -direcao

    p.setPosicao(p.t)
    final = p.posicao
    variacao = final - inicial
    p.rotacao = math.atan2(variacao.y, variacao.x) * 180 / math.pi

def arrow_keys(a_keys: int, x: int, y: int):
    global Personagens
    personagem:InstanciaBZ = Personagens[0]

    if a_keys == GLUT_KEY_UP:
        print('Mudando de direcao')
        personagem.speed = SPEED         # Se pressionar UP
        personagem.direcao = -personagem.direcao

    if a_keys == GLUT_KEY_DOWN:       # Se pressionar DOWN
        print('Mudando de direcao')
        personagem.speed = SPEED         # Se pressionar UP
        personagem.direcao = -personagem.direcao
    
    if a_keys == GLUT_KEY_LEFT:       # Se pressionar LEFT
        if personagem.jaEscolheu:
            personagem.troca_a_proxima_curva(1)
            print('Proxima curva trocada: ', personagem.proxCurva[0].id)
    
    if a_keys == GLUT_KEY_RIGHT:      # Se pressionar RIGHT
        if personagem.jaEscolheu:
            personagem.troca_a_proxima_curva(-1)
            print('Proxima curva trocada: ', personagem.proxCurva[0].id)

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
    global MeiaSeta, Mastro, MeiaSetaInimiga
    MeiaSeta.LePontosDeArquivo("MeiaSeta.txt")
    MeiaSetaInimiga.LePontosDeArquivo("MeiaSetaInimiga.txt")
    # Mastro.LePontosDeArquivo("Mastro.txt")

# ***********************************************************************************
# Esta função deve instanciar todos os personagens do cenário
# ***********************************************************************************
def adicionaPersonagem(speed, cor=(255,0,0)):
    global Personagens
    Personagens.append(InstanciaBZ())
    nP:InstanciaBZ = Personagens[-1]
    nP.speed = speed
    nP.cor = cor
    nP.modelo = DesenhaSetaInimiga
    nP.escala = Ponto (.25,.25,.25) 
    nP.setCurva(listaDeCurvas[8])
    nP.curva = listaDeCurvas[randint(0, len(listaDeCurvas)-1)]
    nP.t = .5
    nP.direcao = 1 if randint(0,1) == 0 else -1


def CriaInstancias():
    global Personagens, SPEED

    Personagens.append(InstanciaBZ())
    p0:InstanciaBZ = Personagens[0]
    p0.modelo = DesenhaSeta
    p0.escala = Ponto (.25,.25,.25) 
    p0.cor = (255,255,255)
    p0.rotacao = 0
    p0.posicao = Ponto(0,0)
    p0.setCurva(listaDeCurvas[0])
    p0.principal = True
    p0.speed = SPEED
    
    adicionaPersonagem(speed=.1, cor=cores[0])
    adicionaPersonagem(speed=1, cor=cores[1])
    adicionaPersonagem(speed=.5, cor=cores[2])
    adicionaPersonagem(speed=.25, cor=cores[3])
    adicionaPersonagem(speed=.75, cor=cores[4])
    adicionaPersonagem(speed=.2, cor=cores[5])
    adicionaPersonagem(speed=.3, cor=cores[7])
    adicionaPersonagem(speed=.4, cor=cores[8])
    adicionaPersonagem(speed=.5, cor=cores[9])
    adicionaPersonagem(speed=.6, cor=cores[10])
    # adicionaPersonagem(speed=.7)
    # adicionaPersonagem(speed=.8)
    # adicionaPersonagem(speed=.9)
    # adicionaPersonagem(speed=1.1)

# ***********************************************************************************
def init():
    global Min, Max, Personagens, listaDeCurvas, listaDePontos, proximas_e_anteriores, colidiu
    # Define a cor do fundo da tela (AZUL)
    Personagens = []
    listaDeCurvas = []
    listaDePontos = []
    colidiu = False

    glClearColor(0, 0, 0, 1)
    # CriaCurvas()
    carregaPontos()
    CarregaModelos()
    CriaInstancias()

    zoom:float = 10
    Min = Ponto(-zoom,-zoom)
    Max = Ponto(zoom,zoom)

def animate():
    global angulo, Personagens, colidiu
    if colidiu: return
    # colidiu = checaColisao(Personagens[0])
    for i in range(len(Personagens)):
        mover(Personagens[i])
    glutPostRedisplay()

def checaColisao(personagen:InstanciaBZ):
    global Personagens
    for i in range(len(Personagens)):
        if personagen == Personagens[i]:
            continue
        if personagen.colideCom(Personagens[i]):
            personagen.speed = 0
            Personagens[i].speed = 0
            print("Colisão, fim de jogo")
            print("'r' para reiniciar")
            return True
    return False
# ***********************************************************************************
# Programa Principal
# ***********************************************************************************


glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA)
# Define o tamanho inicial da janela grafica do programa
glutInitWindowSize(750, 750)
glutInitWindowPosition(600, 100)
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