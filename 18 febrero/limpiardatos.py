import pandas as pd
from unidecode import unidecode
 
#Cargar datos
dataset = pd.read_csv('notas_estudiantes.csv')
print(dataset)
 
#limpiar la columna carrera de espacios en blanco, primera en mayuscula y quitar las tildes
dataset["Carrera"] = dataset["Carrera"].apply(lambda x: unidecode(x.strip().title()) if isinstance(x,str)else x)
print(dataset)
 
dataset["Nombre"] = dataset["Nombre"].apply(lambda x: unidecode(x.strip().title()) if isinstance(x,str)else x)
print(dataset)
#Eliminar las filas con nombre,edad,carrera, y notas vacias
dataset = dataset.dropna(subset=["Nombre","Edad","Carrera","Nota1","Nota2","Nota3"])
print(dataset)
#cambiar tpo de dato float a entero
dataset["Edad"]=dataset["Edad"].astype(int)
print(dataset)
#Eliminar duplicados
dataset = dataset.drop_duplicates()
print(dataset)
#Crear funcion para calcular el promedio de la materia
dataset["Promedio"] = dataset[["Nota1","Nota2","Nota3"]].mean(axis=1)
dataset["Promedio"] = dataset["Promedio"].round(1)
print(dataset)
#Funcion para clasificar el promedio en excelente, bueno y regular
def Clasificarpro(prome):
    if prome >= 4.5:
        return "Excelente"
    elif prome >=3.5:
        return "Bueno"
    elif prome >= 2.5:
        return "regular"
    else:
        return "Deficiente"
   
#Llamar la funcion y crear la coumna desempeño
dataset["Desempeño"] = dataset["Promedio"].apply(Clasificarpro)
print(dataset)
 
Nuevo = dataset.to_excel('notas_limpio.xlsx', index=False)