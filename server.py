import os
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), "conecta_aprende.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            edad INTEGER NOT NULL,
            clave TEXT NOT NULL DEFAULT ''
        )
    """)
    # Agregar columna clave si no existe (para bases de datos antiguas)
    try:
        conn.execute("ALTER TABLE usuarios ADD COLUMN clave TEXT NOT NULL DEFAULT ''")
        conn.commit()
    except Exception:
        pass
    conn.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            clave TEXT NOT NULL
        )
    """)
    # Crear admin por defecto si no existe
    existing = conn.execute("SELECT id FROM admins LIMIT 1").fetchone()
    if not existing:
        conn.execute("INSERT INTO admins (usuario, clave) VALUES (?, ?)", ("admin", "admin123"))
    conn.commit()
    conn.close()

# ─── Servir archivos HTML estáticos ───────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "inicio.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(".", filename)

# ─── Registro de usuarios ─────────────────────────────────────────────────────

@app.route("/registro", methods=["POST"])
def registro():
    try:
        datos = request.json
        if not datos.get("nombre") or not datos.get("edad") or not datos.get("clave"):
            return jsonify({"ok": False, "mensaje": "Nombre, edad y contraseña son obligatorios"}), 400

        conn = get_db()
        conn.execute("INSERT INTO usuarios (nombre, edad, clave) VALUES (?, ?, ?)",
                     (datos["nombre"], int(datos["edad"]), datos["clave"]))
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "mensaje": "Usuario registrado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Login administrador ──────────────────────────────────────────────────────

@app.route("/admin/login", methods=["POST"])
def login_admin():
    try:
        datos = request.json
        conn = get_db()
        admin = conn.execute(
            "SELECT id FROM admins WHERE usuario = ? AND clave = ?",
            (datos.get("usuario"), datos.get("clave"))
        ).fetchone()
        conn.close()
        return jsonify({"login": admin is not None})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── CRUD Admins ──────────────────────────────────────────────────────────────

@app.route("/admin", methods=["POST"])
def crear_admin():
    try:
        datos = request.json
        if not datos.get("usuario") or not datos.get("clave"):
            return jsonify({"ok": False, "mensaje": "Usuario y clave son obligatorios"}), 400

        conn = get_db()
        conn.execute("INSERT INTO admins (usuario, clave) VALUES (?, ?)",
                     (datos["usuario"], datos["clave"]))
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "mensaje": "Administrador creado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admins", methods=["GET"])
def obtener_admins():
    try:
        conn = get_db()
        rows = conn.execute("SELECT id, usuario, clave FROM admins").fetchall()
        conn.close()
        return jsonify([{"id": str(r["id"]), "usuario": r["usuario"], "clave": r["clave"]} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/<id>", methods=["PUT"])
def editar_admin(id):
    try:
        datos = request.json
        conn = get_db()
        conn.execute("UPDATE admins SET usuario = ?, clave = ? WHERE id = ?",
                     (datos.get("usuario"), datos.get("clave"), int(id)))
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "mensaje": "Administrador actualizado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/<id>", methods=["DELETE"])
def eliminar_admin(id):
    try:
        conn = get_db()
        conn.execute("DELETE FROM admins WHERE id = ?", (int(id),))
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "mensaje": "Administrador eliminado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── CRUD Usuarios ────────────────────────────────────────────────────────────

@app.route("/usuario", methods=["POST"])
def crear_usuario():
    try:
        datos = request.json
        if not datos.get("nombre") or not datos.get("edad"):
            return jsonify({"ok": False, "mensaje": "Nombre y edad son obligatorios"}), 400

        conn = get_db()
        conn.execute("INSERT INTO usuarios (nombre, edad) VALUES (?, ?)",
                     (datos["nombre"], int(datos["edad"])))
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "mensaje": "Usuario creado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/usuarios", methods=["GET"])
def obtener_usuarios():
    try:
        conn = get_db()
        rows = conn.execute("SELECT id, nombre, edad, clave FROM usuarios").fetchall()
        conn.close()
        return jsonify([{"id": str(r["id"]), "nombre": r["nombre"], "edad": r["edad"], "clave": r["clave"]} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/usuario/<id>", methods=["PUT"])
def editar_usuario(id):
    try:
        datos = request.json
        conn = get_db()
        conn.execute("UPDATE usuarios SET nombre = ?, edad = ?, clave = ? WHERE id = ?",
                     (datos.get("nombre"), int(datos.get("edad")), datos.get("clave", ""), int(id)))
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "mensaje": "Usuario actualizado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/usuario/<id>", methods=["DELETE"])
def eliminar_usuario(id):
    try:
        conn = get_db()
        conn.execute("DELETE FROM usuarios WHERE id = ?", (int(id),))
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "mensaje": "Usuario eliminado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Inicializar base de datos al arrancar (funciona con python directo y gunicorn)
init_db()

# ─── Inicio ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
