import subprocess
from pathlib import Path
from db.database import database_exists, create_database, ip_exists
from config.settings import settings
from utils.shodan_client import ShodanClient

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
    shodan_client = ShodanClient()
    if not database_exists():
        create_database()

    print("[*] Ejecutando psad_blocker.sh...")
    run_blacklist_script()
    print("[+] Script ejecutado")

    print("[*] Leyendo fichero de blacklist...")
    ips = read_blacklist_file()

    print("[*] Comprobando IPs en base de datos...")

    for ip in ips:
        if ip_exists(ip):
            # IP conocida → solo actualizamos last_seen
            update_last_seen(ip)
            continue

        # IP nueva → UNA llamada a Shodan
        shodan_data = shodan_client.lookup_ip(ip)

        if shodan_data:
            insert_ip(
                ip=ip,
                country=shodan_data.get("country"),
                city=shodan_data.get("city"),
                org=shodan_data.get("org"),
                isp=shodan_data.get("isp"),
                last_seen=shodan_data.get("last_seen"),
                shodan_data=shodan_data.get("raw"),
            )
        else:
            insert_ip(
                ip=ip,
                last_seen=datetime.utcnow().isoformat(),
            )


if __name__ == "__main__":
    main()
