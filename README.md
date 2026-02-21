# VenePay

Pequeña aplicación Flask para procesar pagos en VES y transferencias P2P.

## Qué incluye
- `app.py` — Flask app
- `templates/` — plantillas HTML
- `utils/`, `services/` — lógica y utilidades
- `requirements.txt`, `Procfile`, `runtime.txt` — listo para deploy

## Preparar repo local
```bash
# desde la carpeta del proyecto
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Commit local (hecho automáticamente por el asistente)
El repo local fue inicializado y comiteado con el mensaje `Prepare app for deploy`.

## Deploy recomendado (Render / Railway)
1. Empuja el repo a GitHub.
2. Crea un servicio en Render conectado al repo.
3. Variables de entorno recomendadas:
   - `SECRET_KEY` (string seguro)
   - `FLASK_DEBUG=0`
4. Start command: `gunicorn app:app --workers 3 --bind 0.0.0.0:$PORT`

## Demo rápido con ngrok (temporal)
```bash
# en local, arrancar la app
python app.py
# en otro terminal
ngrok http 5000
```
Copiar la URL pública de ngrok para demos y generar el QR.

## Generar QR para la URL pública
```bash
pip install qrcode pillow
python -c "import qrcode; img=qrcode.make('https://tu-url-publica'); img.save('venepay_qr.png')"
```

## Notas
- Actualmente la app usa SQLite; para producción usar PostgreSQL y migrar la lógica (puedo ayudarte). 
- Cambia `SECRET_KEY` antes de exponer la app.
