
import os
import unittest
from pathlib import Path

from flask import Flask, redirect, url_for
from flask_login import LoginManager, login_required

from models import db, User


class RoutesTestCase(unittest.TestCase):

    def setUp(self):
        ruta_proyecto = Path(__file__).resolve().parent.parent

        self.app = Flask(
            __name__,
            template_folder=str(ruta_proyecto / "templates")
        )

        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "clave_pruebas"
        self.app.config["SQLALCHEMY_DATABASE_URI"] = os.environ[
            "TEST_DATABASE_URL"
        ]
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["WTF_CSRF_ENABLED"] = False

        db.init_app(self.app)

        login_manager = LoginManager()
        login_manager.init_app(self.app)
        login_manager.login_view = "auth.login"

        @login_manager.user_loader
        def load_user(user_id):
            return db.session.get(User, int(user_id))

        from modulos.auth.routes import auth
        self.app.register_blueprint(auth, url_prefix="/auth")

        @self.app.route("/")
        def inicio():
            return redirect(url_for("juegos"))

        @self.app.route("/juegos")
        @login_required
        def juegos():
            return "Lista de videojuegos"

        self.client = self.app.test_client()

        self.ctx = self.app.app_context()
        self.ctx.push()

        db.create_all()

        self.connection = db.engine.connect()
        self.transaction = self.connection.begin()

        db.session.remove()
        db.session.configure(bind=self.connection)

    def tearDown(self):
        db.session.remove()
        self.transaction.rollback()
        self.connection.close()
        db.session.configure(bind=db.engine)
        self.ctx.pop()

    def test_index_access(self):
        respuesta = self.client.get("/")

        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/juegos", respuesta.headers["Location"])

    def test_login_access(self):
        respuesta = self.client.get("/auth/login")

        self.assertEqual(respuesta.status_code, 200)

    def test_juegos_requires_login(self):
        respuesta = self.client.get("/juegos")

        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(
            "/auth/login",
            respuesta.headers["Location"]
        )

    def test_registro_access(self):
        respuesta = self.client.get("/auth/registro")

        self.assertEqual(respuesta.status_code, 200)


if __name__ == "__main__":
    unittest.main()
