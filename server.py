import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
cliente = MongoClient(MONGODB_URI)
db = cliente["conecta_aprende"]

usuarios = db["usuarios"]
admins = db["admins"]

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
        if not datos.get("nombre") or not datos.get("edad"):
            return jsonify({"ok": False, "mensaje": "Nombre y edad son obligatorios"}), 400

        usuarios.insert_one({
            "nombre": datos["nombre"],
            "edad": int(datos["edad"])
        })
        return jsonify({"ok": True, "mensaje": "Usuario registrado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Login administrador ──────────────────────────────────────────────────────

@app.route("/admin/login", methods=["POST"])
def login_admin():
    try:
        datos = request.json
        admin = admins.find_one({
            "usuario": datos.get("usuario"),
            "clave": datos.get("clave")
        })
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

        admins.insert_one({"usuario": datos["usuario"], "clave": datos["clave"]})
        return jsonify({"ok": True, "mensaje": "Administrador creado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admins", methods=["GET"])
def obtener_admins():
    try:
        data = []
        for a in admins.find():
            data.append({
                "id": str(a["_id"]),
                "usuario": a.get("usuario", ""),
                "clave": a.get("clave", "")
            })
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/<id>", methods=["PUT"])
def editar_admin(id):
    try:
        datos = request.json
        admins.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"usuario": datos.get("usuario"), "clave": datos.get("clave")}}
        )
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

# ─── CRUD Usuarios ────────────────────────────────────────────────────────────

@app.route("/usuario", methods=["POST"])
def crear_usuario():
    try:
        datos = request.json
        if not datos.get("nombre") or not datos.get("edad"):
            return jsonify({"ok": False, "mensaje": "Nombre y edad son obligatorios"}), 400

        usuarios.insert_one({"nombre": datos["nombre"], "edad": int(datos["edad"])})
        return jsonify({"ok": True, "mensaje": "Usuario creado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/usuarios", methods=["GET"])
def obtener_usuarios():
    try:
        data = []
        for u in usuarios.find():
            data.append({
                "id": str(u["_id"]),
                "nombre": u.get("nombre", ""),
                "edad": u.get("edad", "")
            })
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/usuario/<id>", methods=["PUT"])
def editar_usuario(id):
    try:
        datos = request.json
        usuarios.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"nombre": datos.get("nombre"), "edad": int(datos.get("edad"))}}
        )
        return jsonify({"ok": True, "mensaje": "Usuario actualizado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/usuario/<id>", methods=["DELETE"])
def eliminar_usuario(id):
    try:
        usuarios.delete_one({"_id": ObjectId(id)})
        return jsonify({"ok": True, "mensaje": "Usuario eliminado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Inicio ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
