
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path
import os

# Localizar el archivo .env en la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")


# Obtener las credenciales desde las variables de entorno
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME")
}


# Crear una conexión con MySQL
def get_connection():
    connection = mysql.connector.connect(**DB_CONFIG)
    return connection
