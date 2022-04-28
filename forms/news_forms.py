from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired


class PublishForm(FlaskForm):
    author = StringField("Автор", validators=[DataRequired()])
    name = StringField("Название", validators=[DataRequired()])
    content = StringField("Содержание", validators=[DataRequired()])
    file = FileField("Фото", validators=[FileRequired()])
    submit = SubmitField('Опубликовать')
