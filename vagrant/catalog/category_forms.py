from flask_wtf import Form
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length


class CategoryAddForm(Form):
    name = StringField('Name', validators=[DataRequired(), Length(max=40)])
    description = TextAreaField('Description', validators=[Length(max=500)])