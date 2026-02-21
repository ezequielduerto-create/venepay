import requests
from bs4 import BeautifulSoup

def get_bcv_rate():
    """
    Extrae la tasa oficial directamente del sitio del BCV.
    Si falla, devuelve una tasa por defecto para no trancar el sistema.
    """
    url = "https://www.bcv.org.ve/"
    tasa_default = 36.50  # Tasa de emergencia por si falla el internet
    
    try:
        # El BCV a veces bloquea peticiones sin 'User-Agent'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # Quitamos la verificación de SSL porque a veces el certificado del BCV da problemas
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Buscamos el div que contiene el dólar según la estructura del BCV
            # Nota: Esto puede cambiar si el BCV rediseña su web
            rate_element = soup.find("div", {"id": "dolar"}).find("strong")
            if rate_element:
                # El BCV usa coma para decimales, hay que cambiarla a punto
                tasa_str = rate_element.text.strip().replace(',', '.')
                return float(tasa_str)
        
        return tasa_default
    except Exception as e:
        print(f"\n⚠️ No se pudo conectar al BCV (Usando tasa default: {tasa_default})")
        return tasa_default

def calcular_monto_ves(monto_usd: float):
    tasa = get_bcv_rate()
    monto_ves = monto_usd * tasa
    return round(monto_ves, 2), tasa