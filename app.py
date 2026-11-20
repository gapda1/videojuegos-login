
import os
import logging
from logging.handlers import RotatingFileHandler

from flask import (
    Flask, render_template, request,
    redirect, url_for, abort, jsonify
)
from flask_login import LoginManager, login_required
from werkzeug.exceptions import HTTPException
from models import db, User
import controllers


app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)


login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "auth.login"
login_manager.login_message = "Debes iniciar sesión para continuar."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


from modulos.auth.routes import auth
app.register_blueprint(auth, url_prefix="/auth")

from api.routes import api
app.register_blueprint(api, url_prefix="/api")


with app.app_context():
    db.create_all()


log_handler = RotatingFileHandler(
    "errors.log",
    maxBytes=1024 * 1024,
    backupCount=3,
    encoding="utf-8"
)

log_handler.setLevel(logging.ERROR)

log_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
))

app.logger.addHandler(log_handler)
app.logger.setLevel(logging.ERROR)



@app.errorhandler(400)
def error_400(error):
    return render_template("400.html"), 400


@app.errorhandler(404)
def error_404(error):

    if request.path.startswith("/api/"):
        return jsonify({
            "codigo": 404,
            "error": "Not Found",
            "mensaje": "El recurso solicitado no existe"
        }), 404

    return render_template("404.html"), 404


@app.errorhandler(405)
def error_405(error):

    if request.path.startswith("/api/"):
        respuesta = jsonify({
            "codigo": 405,
            "error": "Method Not Allowed",
            "mensaje": "El método HTTP no está permitido"
        }), 405

        return respuesta

    return render_template("405.html"), 405


@app.errorhandler(500)
def error_500(error):
    db.session.rollback()

    app.logger.error(
        "Error interno del servidor",
        exc_info=True
    )

    return render_template("500.html"), 500



@app.errorhandler(HTTPException)
def manejar_error_http(error):

    if request.path.startswith("/api/"):
        respuesta = jsonify({
            "error": error.name,
            "mensaje": error.description,
            "codigo": error.code
        })

        return respuesta, error.code

    if error.code == 400:
        return error_400(error)

    if error.code == 404:
        return error_404(error)

    if error.code == 405:
        return error_405(error)

    return error



@app.route("/")
def inicio():
    return redirect(url_for("juegos"))


@app.route("/juegos")
@login_required
def juegos():
    lista_juegos = controllers.obtener_juegos()

    return render_template(
        "juegos.html",
        juegos=lista_juegos
    )


@app.route("/agregar_juego")
@login_required
def formulario_agregar_juego():
    return render_template("agregar_juego.html")


@app.route("/guardar_juego", methods=["POST"])
@login_required
def guardar_juego():
    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]
    precio = request.form["precio"]

    controllers.insertar_juego(
        nombre,
        descripcion,
        precio
    )

    return redirect(url_for("juegos"))


@app.route("/eliminar_juego/<int:id>", methods=["POST"])
@login_required
def eliminar_juego(id):
    controllers.eliminar_juego(id)

    return redirect(url_for("juegos"))


@app.route("/editar_juego/<int:id>")
@login_required
def editar_juego(id):
    juego = controllers.obtener_juego_por_id(id)

    if juego is None:
        abort(404)

    return render_template(
        "editar_juego.html",
        juego=juego
    )


@app.route("/actualizar_juego", methods=["POST"])
@login_required
def actualizar_juego():
    id = request.form["id"]
    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]
    precio = request.form["precio"]

    controllers.actualizar_juego(
        nombre,
        descripcion,
        precio,
        id
    )

    return redirect(url_for("juegos"))




@app.route("/prueba-error-400")
def prueba_error_400():
    abort(400)


@app.route("/prueba-error-500")
def prueba_error_500():
    resultado = 1 / 0
    return str(resultado)


if __name__ == "__main__":
    app.run(debug=False)
