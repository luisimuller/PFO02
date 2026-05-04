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
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    min-height: 100vh;
    background: #fdf0f5;
    font-family: 'DM Sans', sans-serif;
    display: flex;
    align-items: stretch;
  }
  .left {
    width: 45%;
    background: #e8a0b8;
    padding: 60px 48px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .left .tag {
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #7a2d4e;
    font-weight: 500;
  }
  .left h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    color: #2d0f1e;
    line-height: 1.15;
    margin-top: 40px;
  }
  .left .sub {
    margin-top: 16px;
    font-size: 0.9rem;
    color: #6b2040;
    line-height: 1.6;
  }
  .left .footer {
    font-size: 0.75rem;
    color: #a05070;
    letter-spacing: 0.5px;
  }
  .right {
    width: 55%;
    padding: 60px 48px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 16px;
  }
  .right .section-label {
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #c2527a;
    margin-bottom: 8px;
    font-weight: 500;
  }
  .endpoint-card {
    background: #fff;
    border: 1.5px solid #f4c2d8;
    border-radius: 16px;
    padding: 18px 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .endpoint-left {
    display: flex;
    align-items: center;
    gap: 14px;
  }
  .badge {
    font-size: 10px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 6px;
    letter-spacing: 0.5px;
  }
  .post { background: #f4c2d8; color: #8c2d52; }
  .get  { background: #d4f0e4; color: #1a6e47; }
  .route {
    font-family: monospace;
    font-size: 1rem;
    color: #2d1a24;
    font-weight: 500;
  }
  .desc {
    font-size: 0.78rem;
    color: #b090a0;
  }
</style>
</head>
<body>
  <div class="left">
    <div>
      <p class="tag">PFO 2 · Prog. sobre Redes</p>
      <h1>Gestión de Tareas</h1>
      <p class="sub">API REST con autenticación segura y persistencia de datos con SQLite.</p>
    </div>
    <p class="footer">Tecnicatura Superior en Desarrollo de Software · 2026</p>
  </div>
  <div class="right">
    <p class="section-label">Endpoints disponibles</p>
    <div class="endpoint-card">
      <div class="endpoint-left">
        <span class="badge post">POST</span>
        <span class="route">/registro</span>
      </div>
      <span class="desc">Crear cuenta nueva</span>
    </div>
    <div class="endpoint-card">
      <div class="endpoint-left">
        <span class="badge post">POST</span>
        <span class="route">/login</span>
      </div>
      <span class="desc">Iniciar sesión</span>
    </div>
    <div class="endpoint-card">
      <div class="endpoint-left">
        <span class="badge get">GET</span>
        <span class="route">/tareas</span>
      </div>
      <span class="desc">Página de bienvenida</span>
    </div>
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
    print(" Base de datos inicializada.")
    print(" Servidor corriendo en http://127.0.0.1:8000")
    app.run(debug=False, port=8000)
