
import os
import unittest
from decimal import Decimal

from flask import Flask
from models import db, Juego


class ModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)

        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = os.environ[
            "TEST_DATABASE_URL"
        ]
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        db.init_app(self.app)

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

    def test_juego_creation(self):
        juego = Juego(
            nombre="Test",
            descripcion="Desc",
            precio=Decimal("9.99")
        )

        db.session.add(juego)
        db.session.flush()

        self.assertIsNotNone(db.session.get(Juego, juego.id))
        self.assertEqual(juego.nombre, "Test")
        self.assertEqual(juego.precio, Decimal("9.99"))


if __name__ == "__main__":
    unittest.main()
