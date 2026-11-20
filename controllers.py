from models import db, Juego


def obtener_juegos():
    return Juego.query.all()


def obtener_juego_por_id(id):
    return db.session.get(Juego, int(id))


def insertar_juego(nombre, descripcion, precio):
    nuevo_juego = Juego(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio
    )

    db.session.add(nuevo_juego)
    db.session.commit()


# ACTUALIZAR VIDEOJUEGO
def actualizar_juego(nombre, descripcion, precio, id):
    juego = db.session.get(Juego, int(id))

    if juego:
        juego.nombre = nombre
        juego.descripcion = descripcion
        juego.precio = precio

        db.session.commit()


def eliminar_juego(id):
    juego = db.session.get(Juego, int(id))

    if juego:
        db.session.delete(juego)
        db.session.commit()
