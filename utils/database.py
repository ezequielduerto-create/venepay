import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('pagos_vzla.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cedula TEXT NOT NULL,
            telefono_destino TEXT NOT NULL,
            banco_nombre TEXT,
            monto_usd REAL,
            monto_ves REAL,
            tasa_bcv REAL,
            referencia TEXT UNIQUE,
            fecha TEXT,
            estatus TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fondos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monto_ves REAL NOT NULL,
            fecha TEXT,
            descripcion TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            balance REAL DEFAULT 0,
            fecha_registro TEXT
        )
    ''')
    # Insert default admin if not exists
    cursor.execute("INSERT OR IGNORE INTO admin (username, password) VALUES ('admin', 'admin123')")
    conn.commit()
    conn.close()

def registrar_pago(datos):
    conn = sqlite3.connect('pagos_vzla.db')
    cursor = conn.cursor()
    query = '''
        INSERT INTO transacciones (cedula, telefono_destino, banco_nombre, monto_usd, monto_ves, tasa_bcv, referencia, fecha, estatus)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(query, (
        datos['cedula'], datos['destino'], datos['banco'],
        datos['monto_usd'], datos['monto_ves'], datos['tasa'],
        datos['referencia'], datos['fecha'], 'APROBADO'
    ))
    conn.commit()
    conn.close()

def get_total_fondos():
    conn = sqlite3.connect('pagos_vzla.db')
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(monto_ves) FROM fondos")
    total = cursor.fetchone()[0] or 0
    conn.close()
    return total

def agregar_fondos(monto_ves, descripcion):
    conn = sqlite3.connect('pagos_vzla.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO fondos (monto_ves, fecha, descripcion) VALUES (?, ?, ?)",
                   (monto_ves, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), descripcion))
    conn.commit()
    conn.close()

def reducir_fondos(monto_ves):
    total = get_total_fondos()
    if total >= monto_ves:
        # Simplemente agregamos una entrada negativa para reducir
        agregar_fondos(-monto_ves, "Pago realizado")
        return True
    return False

def verificar_admin(username, password):
    conn = sqlite3.connect('pagos_vzla.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def registrar_usuario(username, password, email):
    conn = sqlite3.connect('pagos_vzla.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (username, password, email, balance, fecha_registro) VALUES (?, ?, ?, 0, ?)",
                       (username, password, email, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_balance(username):
    conn = sqlite3.connect('pagos_vzla.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM usuarios WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def transferir_dinero(remitente_username, destinatario_email, monto):
    conn = sqlite3.connect('pagos_vzla.db')
    cursor = conn.cursor()
    
    # Verificar balance del remitente
    cursor.execute("SELECT balance FROM usuarios WHERE username = ?", (remitente_username,))
    remitente_balance = cursor.fetchone()
    if not remitente_balance or remitente_balance[0] < monto:
        conn.close()
        return False, "Fondos insuficientes"
    
    # Verificar que el destinatario existe
    cursor.execute("SELECT username FROM usuarios WHERE email = ?", (destinatario_email,))
    destinatario = cursor.fetchone()
    if not destinatario:
        conn.close()
        return False, "Correo electrónico no registrado"
    
    # Realizar la transferencia
    cursor.execute("UPDATE usuarios SET balance = balance - ? WHERE username = ?", (monto, remitente_username))
    cursor.execute("UPDATE usuarios SET balance = balance + ? WHERE email = ?", (monto, destinatario_email))
    
    # Registrar la transacción
    cursor.execute("INSERT INTO transacciones (cedula, telefono_destino, banco_nombre, monto_usd, monto_ves, referencia, fecha, estatus) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (remitente_username, destinatario_email, 'Transferencia', 0, monto, f'TRANSFER-{remitente_username}', datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'APROBADO'))
    
    conn.commit()
    conn.close()
    return True, f"Transferencia exitosa a {destinatario[0]}"

def verificar_email_existente(email):
    conn = sqlite3.connect('pagos_vzla.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def verificar_usuario(username, password):
    conn = sqlite3.connect('pagos_vzla.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user