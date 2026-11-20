
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from modulos.auth.forms import LoginForm, RegistroForm

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("juegos"))

    form = LoginForm()

    if form.validate_on_submit():
        usuario = User.query.filter_by(
            username=form.username.data
        ).first()

        if usuario and usuario.check_password(form.password.data):
            login_user(usuario)
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for("juegos"))

        flash("Usuario o contraseña incorrectos", "danger")

    return render_template("login.html", form=form)


@auth.route("/registro", methods=["GET", "POST"])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for("juegos"))

    form = RegistroForm()

    if form.validate_on_submit():
        existente = User.query.filter_by(
            username=form.username.data
        ).first()

        if existente:
            flash("Ese usuario ya existe", "warning")
        else:
            nuevo_usuario = User(username=form.username.data)
            nuevo_usuario.set_password(form.password.data)

            db.session.add(nuevo_usuario)
            db.session.commit()

            flash("Usuario registrado correctamente", "success")
            return redirect(url_for("auth.login"))

    return render_template("registro.html", form=form)


@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión correctamente", "success")
    return redirect(url_for("auth.login"))
