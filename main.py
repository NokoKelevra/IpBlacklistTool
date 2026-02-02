from db.database import database_exists, create_database
from config.settings import settings

def init_database():
    if not database_exists():
        print("[+] Base de datos no encontrada. Creando base de datos...")
        create_database()
        print("[+] Base de datos creada correctamente.")
    else:
        print("[+] Base de datos encontrada.")

def main():
    print("Configuración correcta, seguimos...")
    init_database()
    # Aquí irá después:
    # - ejecución del script bash
    # - lectura de la blacklist
    # - consulta a Shodan


if __name__ == "__main__":
    main()
