
from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request
from models import db, Juego

api = Blueprint("api", __name__)


def juego_a_json(juego):
    return {
        "id": juego.id,
        "nombre": juego.nombre,
        "descripcion": juego.descripcion,
        "precio": float(juego.precio)
    }


def validar_juego(datos):
    if not isinstance(datos, dict):
        return None, "Debes enviar un objeto JSON válido"

    nombre = datos.get("nombre")
    descripcion = datos.get("descripcion")
    precio = datos.get("precio")

    if not isinstance(nombre, str) or not nombre.strip():
        return None, "El nombre es obligatorio"

    if not isinstance(descripcion, str) or not descripcion.strip():
        return None, "La descripción es obligatoria"

    if isinstance(precio, bool) or not isinstance(
        precio, (int, float, str)
    ):
        return None, "El precio debe ser numérico"

    try:
        precio = Decimal(str(precio))
    except InvalidOperation:
        return None, "El precio no es válido"

    if not precio.is_finite() or precio < 0 or precio > 9999999.99:
        return None, "El precio está fuera del rango permitido"

    if len(nombre.strip()) > 255 or len(descripcion.strip()) > 255:
        return None, "Nombre o descripción demasiado largos"

    if precio.as_tuple().exponent < -2:
        return None, "El precio admite máximo dos decimales"

    return {
        "nombre": nombre.strip(),
        "descripcion": descripcion.strip(),
        "precio": precio
    }, None



@api.route("/juegos", methods=["GET"])
def listar_juegos():
    juegos = Juego.query.all()

    return jsonify([
        juego_a_json(juego) for juego in juegos
    ]), 200


# GET /api/juegos/<id>
# Obtiene un videojuego por su ID
@api.route("/juegos/<int:id>", methods=["GET"])
def obtener_juego(id):
    juego = db.session.get(Juego, id)

    if juego is None:
        return jsonify({
            "error": "Videojuego no encontrado"
        }), 404

    return jsonify(juego_a_json(juego)), 200



@api.route("/juegos", methods=["POST"])
def crear_juego():
    datos = request.get_json(silent=True)
    valores, error = validar_juego(datos)

    if error:
        return jsonify({"error": error}), 400

    nuevo_juego = Juego(**valores)

    db.session.add(nuevo_juego)
    db.session.commit()

    return jsonify({
        "mensaje": "Videojuego creado correctamente",
        "juego": juego_a_json(nuevo_juego)
    }), 201



@api.route("/juegos/<int:id>", methods=["PUT"])
def actualizar_juego(id):
    juego = db.session.get(Juego, id)

    if juego is None:
        return jsonify({
            "error": "Videojuego no encontrado"
        }), 404

    datos = request.get_json(silent=True)
    valores, error = validar_juego(datos)

    if error:
        return jsonify({"error": error}), 400

    juego.nombre = valores["nombre"]
    juego.descripcion = valores["descripcion"]
    juego.precio = valores["precio"]

    db.session.commit()

    return jsonify({
        "mensaje": "Videojuego actualizado correctamente",
        "juego": juego_a_json(juego)
    }), 200



@api.route("/juegos/<int:id>", methods=["DELETE"])
def eliminar_juego(id):
    juego = db.session.get(Juego, id)

    if juego is None:
        return jsonify({
            "error": "Videojuego no encontrado"
        }), 404

    db.session.delete(juego)
    db.session.commit()

    return "", 204
