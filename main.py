import subprocess
from pathlib import Path
from db.database import database_exists, create_database, ip_exists, insert_ip, update_last_seen, update_last_seen
from config.settings import settings
from utils.shodan_client import ShodanClient
from utils.network import is_ip_active
from datetime import datetime

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

    now = datetime.utcnow().isoformat()

    for ip in ips:
        if not ip_exists(ip):
            # IP nueva → UNA sola llamada a Shodan
            shodan_data = shodan_client.lookup_ip(ip)

            if shodan_data:
                insert_ip(
                    ip=ip,
                    country=shodan_data.get("country"),
                    city=shodan_data.get("city"),
                    org=shodan_data.get("org"),
                    isp=shodan_data.get("isp"),
                    last_seen=now,  # asumimos activa al tener datos
                    shodan_data=shodan_data.get("raw"),
                )
            else:
                insert_ip(
                    ip=ip,
                    last_seen=now,
                )
            continue

        # IP ya conocida → comprobamos actividad real
        if is_ip_active(ip):
            update_last_seen(ip, now)



if __name__ == "__main__":
    main()
