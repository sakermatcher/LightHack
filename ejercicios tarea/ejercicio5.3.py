#Enrique Audrick Burgos Cruz
#A01820613
#ejercicio 3:
def transpuesta_matriz(MatrizA):
    resultado = []
    for j in range(len(MatrizA[0])):
        fila = []
        for i in range(len(MatrizA)):
            fila.append(MatrizA[i][j])
        resultado.append(fila)
    return resultado

def main():
    print("Ejercicio 3: Transpuesta de una matriz")
    print(transpuesta_matriz([[1,2],[3,4]]))
    print(transpuesta_matriz([[1,2,3],[4,5,6]]))
    print(transpuesta_matriz([[7,8],[9,10],[11,12]]))

if __name__ == "__main__":
    main()