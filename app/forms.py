from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class EmailExtractForm(FlaskForm):
    email = TextAreaField("Email", validators=[DataRequired()])
    submit = SubmitField("Extract Signatures")
