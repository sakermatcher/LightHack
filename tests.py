while True: #Pedir input al usuario y verificar que sea un numero
    n= input("Lado= ")

    if n.isdigit():
        n= int(n)
        break


for i in range(n): #Print Cuadrado
    for j in range(n):
        if i == 0 or i == n-1 or j == 0 or j == n-1:
            print('* ', end="")
        else:
            print('  ', end="")
    print()
    

print("")

for i in range(1, n+1): #Print Triangulo
    for space in range(n-i):
        print(' ', end="")
    for star in range(i):
        if star == 0 or i == n or star == i-1:
            print('* ', end="")
        else:
            print('  ', end="")
    print()

print("\n\nCON WHILES:\n")

i= 0
while i < n: #Print Cuandrado
    j= 0
    while j < n:
        if i == 0 or i == n-1 or j == 0 or j == n-1:
            print('* ', end="")
        else:
            print('  ', end="")
        j+= 1
    print()
    i+= 1

print()

i= 1
while i <= n: #Print triangulo
    space= 0
    while space < n-i:
        print(' ', end="")
        space+= 1
    star= 0
    while star < i:
        if star == 0 or i == n or star == i-1:
            print('* ', end="")
        else:
            print('  ', end="")
        star+= 1
    print()
    i+= 1
