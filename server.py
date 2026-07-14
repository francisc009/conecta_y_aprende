import os
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

cliente = MongoClient("mongodb://localhost:27017/")
db = cliente["conecta_aprende"]

usuarios = db["usuarios"]
admins   = db["admins"]
progreso = db["progreso"]

def init_db():
    usuarios.create_index([("nombre", ASCENDING)], unique=True)
    progreso.create_index(
        [("usuario_id", ASCENDING), ("modulo", ASCENDING)],
        unique=True
    )
    if admins.count_documents({}) == 0:
        admins.insert_one({"usuario": "admin", "clave": "admin123"})

def init_db():
    usuarios.create_index([("nombre", ASCENDING)], unique=True)
    progreso.create_index(
        [("usuario_id", ASCENDING), ("modulo", ASCENDING)],
        unique=True
    )
    if admins.count_documents({}) == 0:
        admins.insert_one({"usuario": "admin", "clave": "admin123"})

# ─── Archivos estáticos ────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "inicio.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(".", filename)

# ─── Registro de usuarios ──────────────────────────────────────────────────────

@app.route("/registro", methods=["POST"])
def registro():
    try:
        datos = request.json
        if not datos.get("nombre") or not datos.get("edad") or not datos.get("clave"):
            return jsonify({"ok": False, "mensaje": "Todos los campos son obligatorios"}), 400

        try:
            result = usuarios.insert_one({
                "nombre": datos["nombre"],
                "edad": int(datos["edad"]),
                "clave": datos["clave"]
            })
        except DuplicateKeyError:
            return jsonify({"ok": False, "mensaje": "El nombre de usuario ya existe"}), 409

        return jsonify({"ok": True, "mensaje": "Usuario registrado", "id": str(result.inserted_id), "nombre": datos["nombre"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Login usuarios ────────────────────────────────────────────────────────────

@app.route("/usuario/login", methods=["POST"])
def login_usuario():
    try:
        datos = request.json
        u = usuarios.find_one({"nombre": datos.get("nombre"), "clave": datos.get("clave")})
        if u:
            return jsonify({"ok": True, "id": str(u["_id"]), "nombre": u["nombre"]})
        return jsonify({"ok": False, "mensaje": "Nombre o contraseña incorrectos"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Login administrador ───────────────────────────────────────────────────────

@app.route("/admin/login", methods=["POST"])
def login_admin():
    try:
        datos = request.json
        admin = admins.find_one({"usuario": datos.get("usuario"), "clave": datos.get("clave")})
        return jsonify({"login": admin is not None})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── CRUD Admins ───────────────────────────────────────────────────────────────

@app.route("/admin", methods=["POST"])
def crear_admin():
    try:
        datos = request.json
        if not datos.get("usuario") or not datos.get("clave"):
            return jsonify({"ok": False, "mensaje": "Usuario y clave son obligatorios"}), 400
        admins.insert_one({"usuario": datos["usuario"], "clave": datos["clave"]})
        return jsonify({"ok": True, "mensaje": "Administrador creado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admins", methods=["GET"])
def obtener_admins():
    try:
        rows = list(admins.find({}))
        return jsonify([{"id": str(r["_id"]), "usuario": r["usuario"], "clave": r["clave"]} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/<id>", methods=["PUT"])
def editar_admin(id):
    try:
        datos = request.json
        admins.update_one({"_id": ObjectId(id)}, {"$set": {"usuario": datos.get("usuario"), "clave": datos.get("clave")}})
        return jsonify({"ok": True, "mensaje": "Administrador actualizado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/<id>", methods=["DELETE"])
def eliminar_admin(id):
    try:
        admins.delete_one({"_id": ObjectId(id)})
        return jsonify({"ok": True, "mensaje": "Administrador eliminado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── CRUD Usuarios ─────────────────────────────────────────────────────────────

@app.route("/usuario", methods=["POST"])
def crear_usuario():
    try:
        datos = request.json
        if not datos.get("nombre") or not datos.get("edad"):
            return jsonify({"ok": False, "mensaje": "Nombre y edad son obligatorios"}), 400
        try:
            usuarios.insert_one({"nombre": datos["nombre"], "edad": int(datos["edad"]), "clave": datos.get("clave", "")})
        except DuplicateKeyError:
            return jsonify({"ok": False, "mensaje": "El nombre de usuario ya existe"}), 409
        return jsonify({"ok": True, "mensaje": "Usuario creado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/usuarios", methods=["GET"])
def obtener_usuarios():
    try:
        rows = list(usuarios.find({}))
        return jsonify([{"id": str(r["_id"]), "nombre": r["nombre"], "edad": r["edad"], "clave": r.get("clave", "")} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/usuario/<id>", methods=["PUT"])
def editar_usuario(id):
    try:
        datos = request.json
        usuarios.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"nombre": datos.get("nombre"), "edad": int(datos.get("edad")), "clave": datos.get("clave", "")}}
        )
        return jsonify({"ok": True, "mensaje": "Usuario actualizado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/usuario/<id>", methods=["DELETE"])
def eliminar_usuario(id):
    try:
        usuarios.delete_one({"_id": ObjectId(id)})
        progreso.delete_many({"usuario_id": id})
        return jsonify({"ok": True, "mensaje": "Usuario eliminado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Progreso ──────────────────────────────────────────────────────────────────

@app.route("/progreso", methods=["POST"])
def guardar_progreso():
    try:
        datos = request.json
        usuario_id = datos["usuario_id"]
        modulo = int(datos["modulo"])
        puntaje = int(datos["puntaje"])
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

        existente = progreso.find_one({"usuario_id": usuario_id, "modulo": modulo})
        if existente:
            if puntaje > existente["puntaje"]:
                progreso.update_one(
                    {"usuario_id": usuario_id, "modulo": modulo},
                    {"$set": {"puntaje": puntaje, "fecha": fecha}}
                )
        else:
            progreso.insert_one({"usuario_id": usuario_id, "modulo": modulo, "puntaje": puntaje, "fecha": fecha})

        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/progreso/<usuario_id>", methods=["GET"])
def obtener_progreso(usuario_id):
    try:
        rows = list(progreso.find({"usuario_id": usuario_id}, {"_id": 0, "modulo": 1, "puntaje": 1, "fecha": 1}).sort("modulo", ASCENDING))
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Inicio ────────────────────────────────────────────────────────────────────

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)