from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# Conexión a MongoDB
cliente = MongoClient("mongodb://localhost:27017/")
db = cliente["conecta_aprende"]

usuarios = db["usuarios"]
admins = db["admins"]

# Ruta principal
@app.route("/")
def home():
    return "Servidor Flask funcionando"

# Registro de usuarios
@app.route("/registro", methods=["POST"])
def registro():
    datos = request.json

    usuarios.insert_one({
        "nombre": datos["nombre"],
        "edad": datos["edad"]
    })

    return jsonify({
        "ok": True,
        "mensaje": "Usuario registrado"
    })

# Login administrador
@app.route("/admin", methods=["POST"])
def admin_login():
    datos = request.json

    admin_user = admins.find_one({
        "usuario": datos["usuario"],
        "clave": datos["clave"]
    })

    if admin_user:
        return jsonify({
            "login": True
        })

    return jsonify({
        "login": False
    })

# Ejecutar aplicación
if __name__ == "__main__":
    app.run()