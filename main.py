import subprocess
from pathlib import Path
from db.database import database_exists, create_database, ip_exists, insert_ip, update_last_seen, update_last_seen, get_last_seen
from config.settings import settings
from utils.shodan_client import ShodanClient
from utils.network import is_ip_active
from datetime import datetime, timedelta
from utils.logger import setup_logging

def send_notify(summary: dict):
    message = (
        "IP Blacklist Tool - Resumen\n"
        f"IPs totales: {summary['ips_total']}\n"
        f"Nuevas: {summary['ips_new']}\n"
        f"Comprobadas: {summary['ips_checked']}\n"
        f"Activas: {summary['ips_active']}\n"
        f"Errores: {summary['errors']}"
    )

    subprocess.run(
        ["notify"],
        input=message,
        text=True,
        check=False
    )


def should_check_activity(last_seen: str | None, hours: int = 24) -> bool:
    if last_seen is None:
        return True

    last = datetime.fromisoformat(last_seen)
    return datetime.utcnow() - last > timedelta(hours=hours)

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
    shodan_client = ShodanClient()
    execution_summary = {
        "ips_total": 0,
        "ips_new": 0,
        "ips_checked": 0,
        "ips_active": 0,
        "errors": 0,
    }

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
        execution_summary["ips_total"] += 1
        if not ip_exists(ip):
            execution_summary["ips_new"] += 1
            logger.info(f"IP nueva detectada: {ip}")
            shodan_data = shodan_client.lookup_ip(ip)

            if shodan_data:
                insert_ip(
                    ip=ip,
                    country=shodan_data.get("country"),
                    city=shodan_data.get("city"),
                    org=shodan_data.get("org"),
                    isp=shodan_data.get("isp"),
                    last_seen=now,
                    shodan_data=shodan_data.get("raw"),
                )
            else:
                insert_ip(ip=ip)
            continue
        execution_summary["ips_checked"] += 1
        last_seen = get_last_seen(ip)

        if should_check_activity(last_seen):
            if is_ip_active(ip):
                execution_summary["ips_active"] += 1
                update_last_seen(ip, now)
                logger.info(f"IP activa confirmada: {ip}")

    send_notify(execution_summary)

if __name__ == "__main__":
    logger = setup_logging()
    logger.info("Inicio de ejecución")
    try:
        main()
    except Exception as e:
        logger.exception("Error fatal en la ejecución")
        execution_summary["errors"] += 1
