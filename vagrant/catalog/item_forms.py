from flask_wtf import Form
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length


class ItemAddForm(Form):
    name = StringField('Name', validators=[DataRequired(), Length(max=40)])
    category = SelectField('Category', validators=[], coerce=int)
    description = TextAreaField('Description', validators=[Length(max=500)])


class ItemEditForm(Form):
    name = StringField('Name', validators=[DataRequired(), Length(max=40)])
    category = SelectField('Category', validators=[], coerce=int)
    description = TextAreaField('Description', validators=[Length(max=500)])


class ItemDeleteForm(Form):
    pass
