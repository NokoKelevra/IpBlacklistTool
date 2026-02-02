import shodan
from shodan.exception import APIError

from config.settings import settings


class ShodanClient:
    def __init__(self):
        self.api = shodan.Shodan(settings.SHODAN_API_KEY)

    def lookup_ip(self, ip: str) -> dict | None:
        """
        Consulta una IP en Shodan.
        Devuelve dict con datos relevantes o None si no existe.
        """
        try:
            result = self.api.host(ip)

            return {
                "ip": ip,
                "country": result.get("country_name"),
                "city": result.get("city"),
                "org": result.get("org"),
                "isp": result.get("isp"),
                "last_seen": result.get("last_update"),
                "raw": result,
            }

        except APIError as e:
            # IP no encontrada en Shodan
            if "No information available" in str(e):
                return None

            # Rate limit u otros errores
            raise RuntimeError(f"Error Shodan para {ip}: {e}")
