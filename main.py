import subprocess

from db.database import database_exists, create_database
from config.settings import settings

def run_blacklist_script():
    """
    Ejecuta el script psad_blocker.sh con sudo.
    Devuelve stdout si todo va bien.
    Lanza excepción si falla.
    """
    try:
        result = subprocess.run(
            ["sudo", settings.BLACKLIST_SCRIPT],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout

    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Error ejecutando psad_blocker.sh\n"
            f"STDOUT:\n{e.stdout}\n"
            f"STDERR:\n{e.stderr}"
        )

def init_database():
    if not database_exists():
        print("[+] Base de datos no encontrada. Creando base de datos...")
        create_database()
        print("[+] Base de datos creada correctamente.")
    else:
        print("[+] Base de datos encontrada.")

def main():
    print("[*] Iniciando aplicación")

    # Validación y DB
    if not database_exists():
        print("[*] Base de datos no existe, creando...")
        create_database()

    print("[*] Ejecutando psad_blocker.sh...")
    output = run_blacklist_script()

    print("[+] Script ejecutado correctamente")
    print("[*] Salida del script:")
    print(output)


if __name__ == "__main__":
    main()
