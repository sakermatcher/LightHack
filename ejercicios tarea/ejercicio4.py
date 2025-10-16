#Enrique Audrick Burgos Cruz
#A01820613
#ejercicio 4:
def interseccion_listas(lista1, lista2):
    return list(set(lista1).intersection( set(lista2)))

def main():
    print("Ejercicio 4: Intersección de dos listas")
    print(interseccion_listas([1, 2, 3], [2, 3, 4]))    
    print(interseccion_listas([5, 6, 7], [7, 8, 9]))    
    print(interseccion_listas([10, 11], [12, 13]))        

if __name__ == "__main__":
    main()
