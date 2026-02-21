# Lista oficial de códigos bancarios de Venezuela
BANCOS_VENEZUELA = {
    "0102": "Banco de Venezuela",
    "0105": "Mercantil",
    "0108": "Provincial",
    "0114": "Bancaribe",
    "0115": "Exterior",
    "0128": "Banco Caroní",
    "0134": "Banesco",
    "0137": "Sofitasa",
    "0138": "Banplus",
    "0151": "BFC (Fondo Común)",
    "0156": "DelSur",
    "0157": "Banavih",
    "0163": "Tesoro",
    "0166": "Agrícola",
    "0168": "Bancrecer",
    "0169": "Mi Banco",
    "0171": "Activo",
    "0172": "Bancamiga",
    "0174": "Banplus",
    "0175": "Bicentenario",
    "0177": "BANFANB",
    "0191": "BNC (Nacional de Crédito)"
}

def listar_bancos():
    print("\n--- BANCOS DISPONIBLES ---")
    for codigo, nombre in BANCOS_VENEZUELA.items():
        print(f"[{codigo}] - {nombre}")