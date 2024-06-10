from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, FileField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class UploadForm(FlaskForm):
    file = FileField("Excel File", validators=[DataRequired()])
    start_row = IntegerField(
        "Start Row", default=0, validators=[DataRequired(), NumberRange(min=0)]
    )
    service_line = StringField(
        "Service Line", default="Consulting", validators=[DataRequired()]
    )
    submit = SubmitField("Upload and Preview")
