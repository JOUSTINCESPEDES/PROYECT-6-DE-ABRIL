import mysql.connector
import pandas as pd

def conectar():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="dashnotas"
    )
    return conexion

#obtener usuarios
def obtenerusuarios(username):
    #conectar a la base bd
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    #buscar el usuario en la bd
    cursor.execute("SELECT * FROM usuarios WHERE username=%s", (username,))
    usuario = cursor.fetchone()
    conn.close()


#obtener los estudiantes
def obtenerestudiantes():

    conn = conectar()
    query = "SELECT * FROM estudiantes"
    df = pd.read_sql(query, conn)
    conn.close()

    
if __name__ == "__main__":
    coon = conectar()
    print("Conexion exitosa")
    coon.close()