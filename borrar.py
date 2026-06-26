from fastapi import Depends

contador = 1

def get_number():
    print("Ejecutando get_number")
    return 10*contador


def suma(x: int = Depends(get_number)):
    global contador
    contador = contador + 1
    print(x)

suma()
print(contador)
suma()
print(contador)
suma()
print(contador)