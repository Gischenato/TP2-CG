for p in open('PontosTaba.txt'):
  x,y = p.split()
  x,y = int(x), int(y)
  print((x-2)*2,(y)*2)