from flask_wtf import FlaskForm
from wtforms import FileField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired


class LoadForm(FlaskForm):
    file = FileField("Upload Excel File", validators=[DataRequired()])
    start_row = IntegerField("Start Row", default=1, validators=[DataRequired()])
    service_line = StringField(
        "Service Line", default="Consulting", validators=[DataRequired()]
    )
    submit = SubmitField("Upload")
