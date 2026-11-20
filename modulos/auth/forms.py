
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField(
        "Usuario",
        validators=[DataRequired()]
    )

    password = PasswordField(
        "Contraseña",
        validators=[DataRequired()]
    )

    submit = SubmitField("Iniciar sesión")


class RegistroForm(FlaskForm):
    username = StringField(
        "Usuario",
        validators=[DataRequired(), Length(min=3, max=80)]
    )

    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(), Length(min=6)]
    )

    confirmar = PasswordField(
        "Confirmar contraseña",
        validators=[
            DataRequired(),
            EqualTo("password", message="Las contraseñas no coinciden")
        ]
    )

    submit = SubmitField("Registrarse")
