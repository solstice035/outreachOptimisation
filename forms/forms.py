# from typing import Optional
from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    FieldList,
    FileField,
    FormField,
    IntegerField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Email, Optional


class UploadForm(FlaskForm):
    file = FileField("Upload Excel File", validators=[DataRequired()])
    start_row = IntegerField("Start Row", default=1, validators=[DataRequired()])
    service_line = StringField(
        "Service Line", default="Consulting", validators=[DataRequired()]
    )
    submit = SubmitField("Upload")


class SingleDelegateForm(FlaskForm):
    delegate_number = StringField("Delegate Number", validators=[DataRequired()])
    delegate_name = StringField("Delegate Name", validators=[DataRequired()])
    delegate_gui = StringField("Delegate GUI", validators=[DataRequired()])
    delegate_email = StringField("Delegate Email", validators=[DataRequired(), Email()])
    end_date = DateField(
        "End Date (Optional)", format="%Y-%m-%d", validators=[Optional()]
    )


class DelegateForm(FlaskForm):
    engagement_id = IntegerField("Engagement ID", validators=[DataRequired()])
    delegates = FieldList(FormField(SingleDelegateForm), min_entries=1, max_entries=10)
    submit = SubmitField("Add Delegates")
