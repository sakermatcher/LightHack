#Enrique Audrick Burgos Cruz
#A01820613
#ejercicio 2:
def multiplicacion_matrices(MatrizA, MatrizB):
    resultado = []
    for i in range(len(MatrizA)):
        fila = []
        for j in range(len(MatrizB[0])):
            suma = 0
            for k in range(len(MatrizB)):
                suma += MatrizA[i][k] * MatrizB[k][j]
            fila.append(suma)
        resultado.append(fila)
    return resultado

def main():
    print("Ejercicio 2: Multiplicación de matrices")
    print(multiplicacion_matrices([[1,2],[3,4]], [[2,0],[1,2]]))
    print(multiplicacion_matrices([[1,0],[0,1]], [[5,6],[7,8]]))
    print(multiplicacion_matrices([[2,1],[0,3]], [[1,2],[3,4]]))

if __name__ == "__main__":
    main()
