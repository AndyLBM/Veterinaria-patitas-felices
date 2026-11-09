
from backend.app.database.connection import get_connection
from mysql.connector import Error


def probar_conexion():

    conexion = None
    cursor = None

    try:
        # 1. Establecer conexión con MySQL
        conexion = get_connection()

        print("Conexion exitosa con MySQL")

        # 2. Crear cursor para ejecutar consultas SQL
        cursor = conexion.cursor()

        # 3. Consultar la base de datos seleccionada
        cursor.execute("SELECT DATABASE()")

        base_datos = cursor.fetchone()

        print("\nBase de datos:", base_datos[0])

        # 4. Consultar las tablas existentes
        cursor.execute("SHOW TABLES")

        tablas = cursor.fetchall()

        print("\nTABLAS REGISTRADAS:\n")

        for tabla in tablas:
            print("-", tabla[0])

        # 5. Consultar la estructura de la tabla mascota
        cursor.execute("DESCRIBE mascota")

        columnas = cursor.fetchall()

        print("\nESTRUCTURA DE LA TABLA MASCOTA:\n")

        for columna in columnas:
            print(columna)

        # 6. Consultar cantidad de mascotas registradas
        cursor.execute("""
            SELECT COUNT(*)
            FROM mascota
        """)

        cantidad = cursor.fetchone()

        print("\nTotal de mascotas registradas:", cantidad[0])

    except Error as error:

        print("\nError al conectar o consultar MySQL:")
        print(error)

    finally:

        # 7. Cerrar cursor
        if cursor is not None:
            cursor.close()

        # 8. Cerrar conexión
        if conexion is not None and conexion.is_connected():
            conexion.close()
            print("\nConexion cerrada correctamente")


if __name__ == "__main__":
    probar_conexion()
