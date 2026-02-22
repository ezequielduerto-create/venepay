from flask import Flask, render_template, request, redirect, url_for, session, flash
from utils.bancos import BANCOS_VENEZUELA
from utils.currency import calcular_monto_ves
from services.pago_movil import PagoMovilProcessor
from utils.database import registrar_pago, init_db, get_total_fondos, agregar_fondos, reducir_fondos, verificar_admin, registrar_usuario, verificar_usuario, get_user_balance, transferir_dinero, verificar_email_existente
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'aK5oI2_t_eccNVOJT3jfheuOv7873xyMmZ05j0FBU34')  # use env var in production

# Inicializar la base de datos
init_db()

@app.route('/')
def index():
    if not session.get('user'):
        return redirect(url_for('login'))
    user_balance = get_user_balance(session['user'])
    return render_template('index.html', user_balance=user_balance)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = verificar_usuario(username, password)
        if user:
            session['user'] = user[1]  # username
            return redirect(url_for('index'))
        else:
            flash('Credenciales incorrectas')
    return render_template('login.html')

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if not session.get('user'):
        return redirect(url_for('login'))
    
    user_balance = get_user_balance(session['user'])
    
    if request.method == 'POST':
        destinatario_email = request.form['destinatario_email']
        monto = float(request.form['monto'])
        
        success, message = transferir_dinero(session['user'], destinatario_email, monto)
        
        if success:
            user_balance = get_user_balance(session['user'])
            return render_template('transfer.html', message=message, success=True, user_balance=user_balance)
        else:
            return render_template('transfer.html', message=message, success=False, user_balance=user_balance)
    
    return render_template('transfer.html', user_balance=user_balance)

@app.route('/user/logout')
def user_logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/procesar', methods=['POST'])
def procesar():
    if not session.get('user'):
        return redirect(url_for('login'))
    try:
        monto_ves = float(request.form['monto_ves'])
        cod_banco = request.form['cod_banco']
        cedula = request.form['cedula'].upper()
        telefono = request.form['telefono']

        # Verificar balance del usuario
        user_balance = get_user_balance(session['user'])
        if user_balance < monto_ves:
            return render_template('index.html', message="Fondos insuficientes en tu cuenta.", success=False, user_balance=user_balance)

        if cod_banco not in BANCOS_VENEZUELA:
            return render_template('index.html', message="Código de banco no reconocido.", success=False, user_balance=user_balance)

        nombre_banco = BANCOS_VENEZUELA[cod_banco]

        # Reducir balance del usuario (simular reducción)
        # Nota: En un sistema real, esto debería ser atómico
        conn = sqlite3.connect('pagos_vzla.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET balance = balance - ? WHERE username = ?", (monto_ves, session['user']))
        conn.commit()
        conn.close()

        procesador = PagoMovilProcessor(banco_comercio="0102", telefono_comercio="04121112233")
        respuesta = procesador.enviar_pago(monto_ves, cedula, telefono, cod_banco)

        datos_transaccion = {
            "cedula": cedula,
            "destino": telefono,
            "banco": nombre_banco,
            "monto_usd": 0,
            "monto_ves": monto_ves,
            "tasa": 0,
            "referencia": respuesta["referencia"],
            "fecha": respuesta["fecha"]
        }

        registrar_pago(datos_transaccion)
        message = f"Pago exitoso de {monto_ves} VES al {nombre_banco}. Ref: {respuesta['referencia']}"
        user_balance = get_user_balance(session['user'])
        return render_template('index.html', message=message, success=True, user_balance=user_balance)

    except Exception as e:
        user_balance = get_user_balance(session['user'])
        return render_template('index.html', message=f"Error: {str(e)}", success=False, user_balance=user_balance)

@app.route('/reporte')
def reporte():
    conn = sqlite3.connect('pagos_vzla.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transacciones ORDER BY id DESC")
    transacciones = cursor.fetchall()
    conn.close()
    return render_template('reporte.html', transacciones=transacciones)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if verificar_admin(username, password):
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash('Credenciales incorrectas')
    return render_template('admin_login.html')

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    total_fondos = get_total_fondos()
    return render_template('admin_panel.html', total_fondos=total_fondos)

@app.route('/admin/distribuir_fondos', methods=['POST'])
def distribuir_fondos():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    try:
        usuario_email = request.form['usuario_email']
        monto_usd = float(request.form['monto_usd'])
        
        # Verificar que el usuario existe
        if not verificar_email_existente(usuario_email):
            flash(f"El correo {usuario_email} no está registrado.")
            return redirect(url_for('admin_panel'))
        
        _, tasa = calcular_monto_ves(1)  # Obtener la tasa actual
        monto_ves = monto_usd * tasa
        
        # Agregar fondos al balance del usuario
        conn = sqlite3.connect('pagos_vzla.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET balance = balance + ? WHERE email = ?", (monto_ves, usuario_email))
        conn.commit()
        conn.close()
        
        # Registrar como transacción administrativa
        datos_transaccion = {
            "cedula": "ADMIN",
            "destino": usuario_email,
            "banco": "ADMIN",
            "monto_usd": monto_usd,
            "monto_ves": monto_ves,
            "tasa": tasa,
            "referencia": f"ADMIN-{usuario_email}",
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        registrar_pago(datos_transaccion)
        
        flash(f"Fondos distribuidos exitosamente: {monto_ves} VES a {usuario_email}")
    except Exception as e:
        flash(f"Error: {str(e)}")
    return redirect(url_for('admin_panel'))

@app.route('/admin/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)