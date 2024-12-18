from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired

class ItemForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired()])
    precio = FloatField("Precio", validators=[DataRequired()])
    inventario = FloatField("Inventario", validators=[DataRequired()])
    categoria = StringField("Categoria", validators=[DataRequired()])
    descripcion = StringField("Descripcion", validators=[DataRequired()])
    link = StringField("Link", validators=[DataRequired()])
    submit = SubmitField("Add/Update Item")