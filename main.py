import subprocess
from pathlib import Path
from db.database import database_exists, create_database, ip_exists
from config.settings import settings

def run_blacklist_script():
    subprocess.run(
        ["sudo", settings.BLACKLIST_SCRIPT],
        check=True
    )

def read_blacklist_file():
    path = Path(settings.BLACKLIST_OUTPUT_FILE)

    if not path.exists():
        raise FileNotFoundError(
            f"No existe el fichero de blacklist: {path}"
        )

    ips = set()

    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                ips.add(line)

    return list(ips)


def init_database():
    if not database_exists():
        print("[+] Base de datos no encontrada. Creando base de datos...")
        create_database()
        print("[+] Base de datos creada correctamente.")
    else:
        print("[+] Base de datos encontrada.")

def main():
    print("[*] Iniciando aplicación")

    if not database_exists():
        create_database()

    print("[*] Ejecutando psad_blocker.sh...")
    run_blacklist_script()
    print("[+] Script ejecutado")

    print("[*] Leyendo fichero de blacklist...")
    ips = read_blacklist_file()

    print("[*] Comprobando IPs en base de datos...")

    new_ips = []
    existing_ips = []

    for ip in ips:
        if ip_exists(ip):
            existing_ips.append(ip)
        else:
            new_ips.append(ip)

    print(f"[+] IPs ya existentes: {len(existing_ips)}")
    print(f"[+] IPs nuevas: {len(new_ips)}")



if __name__ == "__main__":
    main()
