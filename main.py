from utils.bancos import BANCOS_VENEZUELA, listar_bancos
from utils.currency import calcular_monto_ves
from services.pago_movil import PagoMovilProcessor
from utils.database import registrar_pago, init_db

# Inicializar la base de datos
init_db()

def ejecutar_cobro():
    try:
        monto_usd = float(input("\nMonto a cobrar (USD $): "))
        
        # Selección de Banco
        listar_bancos()
        cod_banco = input("Ingrese el CÓDIGO del banco destino (ej. 0134): ")
        
        if cod_banco not in BANCOS_VENEZUELA:
            print("❌ Código de banco no reconocido.")
            return

        nombre_banco = BANCOS_VENEZUELA[cod_banco]
        cedula_paga = input("Cédula/RIF: ").upper()
        tel_paga = input("Teléfono: ")

        monto_ves, tasa_usada = calcular_monto_ves(monto_usd)
        
        print(f"\nEnviando {monto_ves} VES al {nombre_banco}...")

        procesador = PagoMovilProcessor(banco_comercio="0102", telefono_comercio="04121112233")
        respuesta = procesador.enviar_pago(monto_ves, cedula_paga, tel_paga, cod_banco)
        
        datos_transaccion = {
            "cedula": cedula_paga,
            "destino": tel_paga,
            "banco": nombre_banco, # Guardamos el nombre comercial
            "monto_usd": monto_usd,
            "monto_ves": monto_ves,
            "tasa": tasa_usada,
            "referencia": respuesta["referencia"],
            "fecha": respuesta["fecha"]
        }
        
        registrar_pago(datos_transaccion)
        print(f"✅ Transacción exitosa en {nombre_banco}. Ref: {respuesta['referencia']}")

    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    ejecutar_cobro()