#Enrique Audrick Burgos Cruz
#A01820613
#ejercicio 3:
def eliminar_duplicados(lista):
    return list(set(lista))

def main():
    print("Ejercicio 3: Eliminar duplicados de una lista")
    print(eliminar_duplicados([1, 2, 2, 3, 3, 4])) 
    print(eliminar_duplicados([5, 5, 5, 5]))        
    print(eliminar_duplicados([10, 20, 10, 30]))   

if __name__ == "__main__":
    main()

