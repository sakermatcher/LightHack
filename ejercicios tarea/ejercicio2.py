#Enrique Audrick Burgos Cruz
#A01820613
#ejercicio 2:

def mayor_impar(lista):
    impares = [num for num in lista if num % 2 != 0]
    if impares:
        return max(impares)
    else:
        return None  

def main():
    print("Ejercicio 2: Mayor valor impar de una lista")
    print(mayor_impar([2, 3, 5, 8, 10]))    
    print(mayor_impar([1, 7, 9, 14]))       
    print(mayor_impar([2, 4, 6, 8]))        

if __name__ == "__main__":
    main()
