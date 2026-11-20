
import os
import unittest
from decimal import Decimal

from flask import Flask
from models import db, Juego
from api.routes import api


class APITestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)

        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = os.environ[
            "TEST_DATABASE_URL"
        ]
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        db.init_app(self.app)
        self.app.register_blueprint(api, url_prefix="/api")

        self.client = self.app.test_client()

        self.ctx = self.app.app_context()
        self.ctx.push()

        db.create_all()

        self.connection = db.engine.connect()
        self.transaction = self.connection.begin()

        db.session.remove()
        db.session.configure(bind=self.connection)

        juego = Juego(
            nombre="Juego de prueba",
            descripcion="Descripcion de prueba",
            precio=Decimal("100.00")
        )

        db.session.add(juego)
        db.session.flush()

        self.juego_id = juego.id

    def tearDown(self):
        db.session.remove()
        self.transaction.rollback()
        self.connection.close()
        db.session.configure(bind=db.engine)
        self.ctx.pop()

    def test_get_juegos(self):
        respuesta = self.client.get("/api/juegos")

        self.assertEqual(respuesta.status_code, 200)
        self.assertIsInstance(respuesta.get_json(), list)
        self.assertTrue(
    any(
        juego["id"] == self.juego_id
        for juego in respuesta.get_json()
    )
)

    def test_get_juego_por_id(self):
        respuesta = self.client.get(
            f"/api/juegos/{self.juego_id}"
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.get_json()["nombre"],
            "Juego de prueba"
        )

    def test_get_juego_inexistente(self):
        respuesta = self.client.get("/api/juegos/999999999")

        self.assertEqual(respuesta.status_code, 404)

    def test_post_juego_valido(self):
        datos = {
            "nombre": "Minecraft",
            "descripcion": "Juego de construccion",
            "precio": 350.00
        }

        respuesta = self.client.post(
            "/api/juegos",
            json=datos
        )

        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(
            respuesta.get_json()["juego"]["nombre"],
            "Minecraft"
        )

    def test_post_juego_invalido(self):
        datos = {
            "nombre": "",
            "descripcion": "Sin nombre",
            "precio": 100
        }

        respuesta = self.client.post(
            "/api/juegos",
            json=datos
        )

        self.assertEqual(respuesta.status_code, 400)

    def test_put_juego(self):
        datos = {
            "nombre": "Juego actualizado",
            "descripcion": "Nueva descripcion",
            "precio": 200.00
        }

        respuesta = self.client.put(
            f"/api/juegos/{self.juego_id}",
            json=datos
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.get_json()["juego"]["nombre"],
            "Juego actualizado"
        )

    def test_delete_juego(self):
        respuesta = self.client.delete(
            f"/api/juegos/{self.juego_id}"
        )

        self.assertEqual(respuesta.status_code, 204)
        self.assertIsNone(
            db.session.get(Juego, self.juego_id)
        )


if __name__ == "__main__":
    unittest.main()
