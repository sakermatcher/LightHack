#Enrique Audrick Burgos Cruz
#A01820613
#ejercicio 1:
def suma_matrices(MatrizA, MatrizB):
    filas = len(MatrizA)
    columnas = len(MatrizA[0])
    resultado = []
    for i in range(filas):
        fila = []
        for j in range(columnas):
            fila.append(MatrizA[i][j] + MatrizB[i][j])
        resultado.append(fila)
    return resultado

def main():
    print("Ejercicio 1: Suma de matrices")
    print(suma_matrices([[1,2],[3,4]], [[5,6],[7,8]]))      
    print(suma_matrices([[0,1],[1,0]], [[1,0],[0,1]]))      
    print(suma_matrices([[2,3,4],[1,0,5]], [[1,1,1],[2,2,2]])) 

if __name__ == "__main__":
    main()
