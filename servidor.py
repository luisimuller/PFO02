from flask import Flask, request, jsonify, render_template_string
import sqlite3
import bcrypt
import os

app = Flask(__name__)
DB_PATH = "tareas.db"

# ─── HTML de bienvenida ──────────────────────────────────────────────────────
BIENVENIDA_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PFO2 - Gestor de Tareas</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
    }
    .card {
      background: rgba(255,255,255,0.05);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 20px;
      padding: 50px 60px;
      text-align: center;
      backdrop-filter: blur(10px);
      max-width: 650px;
      width: 90%;
    }
    .badge {
      display: inline-block;
      background: rgba(233,69,96,0.2);
      border: 1px solid #e94560;
      color: #e94560;
      font-size: 0.8rem;
      font-weight: bold;
      letter-spacing: 2px;
      padding: 4px 14px;
      border-radius: 20px;
      margin-bottom: 20px;
    }
    h1 { font-size: 2.5rem; margin-bottom: 8px; color: #ffffff; }
    .bienvenida {
      font-size: 1.2rem;
      color: #00d4ff;
      margin: 16px 0 6px;
      font-weight: 600;
    }
    p { color: #aaa; margin: 8px 0; line-height: 1.6; font-size: 0.95rem; }
    .divider {
      border: none;
      border-top: 1px solid rgba(255,255,255,0.1);
      margin: 28px 0;
    }
    .endpoints { text-align: left; }
    .endpoint {
      background: rgba(255,255,255,0.07);
      border-radius: 10px;
      padding: 12px 18px;
      margin: 8px 0;
      font-family: monospace;
      font-size: 0.9rem;
    }
    .method-post { color: #e94560; font-weight: bold; margin-right: 8px; }
    .method-get  { color: #4caf50; font-weight: bold; margin-right: 8px; }
    .route { color: #00d4ff; }
    .footer {
      margin-top: 30px;
      font-size: 0.78rem;
      color: rgba(255,255,255,0.3);
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">PFO 2 — Programacion sobre Redes</div>
    <h1>📋 Gestor de Tareas</h1>
    <p class="bienvenida">¡Bienvenido/a al sistema!</p>
    <p>Este proyecto implementa una API REST con registro de usuarios,<br>
       autenticacion segura y persistencia de datos con SQLite.</p>
    <hr class="divider">
    <div class="endpoints">
      <div class="endpoint"><span class="method-post">POST</span><span class="route">/registro</span> — Crear una cuenta nueva</div>
      <div class="endpoint"><span class="method-post">POST</span><span class="route">/login</span> — Iniciar sesion con tu cuenta</div>
      <div class="endpoint"><span class="method-get">GET</span> <span class="route">/tareas</span> — Esta pagina de bienvenida</div>
    </div>
    <div class="footer">Tecnicatura Superior en Desarrollo de Software &mdash; 2026</div>
  </div>
</body>
</html>
"""

# ─── Base de datos ────────────────────────────────────────────────────────────
def init_db():
    """Crea las tablas si no existen."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario   TEXT    NOT NULL UNIQUE,
            password  TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.route("/registro", methods=["POST"])
def registro():
    """Registra un usuario nuevo con contraseña hasheada."""
    datos = request.get_json()
    if not datos or "usuario" not in datos or "contrasena" not in datos:
        return jsonify({"error": "Se requieren 'usuario' y 'contrasena'"}), 400

    usuario = datos["usuario"].strip()
    contrasena = datos["contrasena"]

    if not usuario or not contrasena:
        return jsonify({"error": "Usuario y contrasena no pueden estar vacios"}), 400

    # Hash con bcrypt (genera salt automáticamente)
    hashed = bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt())

    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO usuarios (usuario, password) VALUES (?, ?)",
            (usuario, hashed.decode("utf-8"))
        )
        conn.commit()
        conn.close()
        return jsonify({"mensaje": f"Usuario '{usuario}' registrado correctamente"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": f"El usuario '{usuario}' ya existe"}), 409


@app.route("/login", methods=["POST"])
def login():
    """Verifica credenciales del usuario."""
    datos = request.get_json()
    if not datos or "usuario" not in datos or "contrasena" not in datos:
        return jsonify({"error": "Se requieren 'usuario' y 'contrasena'"}), 400

    usuario = datos["usuario"].strip()
    contrasena = datos["contrasena"]

    conn = get_db()
    fila = conn.execute(
        "SELECT password FROM usuarios WHERE usuario = ?", (usuario,)
    ).fetchone()
    conn.close()

    if fila is None:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Verificar contrasena contra el hash guardado
    if bcrypt.checkpw(contrasena.encode("utf-8"), fila["password"].encode("utf-8")):
        return jsonify({"mensaje": f"Bienvenido/a, {usuario}!"}), 200
    else:
        return jsonify({"error": "Contraseña incorrecta"}), 401


@app.route("/tareas", methods=["GET"])
def tareas():
    """Devuelve la página HTML de bienvenida."""
    return render_template_string(BIENVENIDA_HTML)


# ─── Arranque ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("✅ Base de datos inicializada.")
    print("🚀 Servidor corriendo en http://127.0.0.1:8000")
    app.run(debug=False, port=8000)
