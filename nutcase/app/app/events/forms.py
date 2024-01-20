from flask_wtf import FlaskForm
# StringField, SelectField, SubmitField, IntegerField, BooleanField # TextAreaField
from wtforms import SelectField, SubmitField
# from wtforms.validators import ValidationError, DataRequired, Length

class Events_Form(FlaskForm):
    Event_Level = SelectField(u'Level', choices=[
                (20,    "Info"),
                (30, "Warning"),
                (40,   "Alert"),
                ], 
                # default=('alert', "Alert")
                coerce=int
                )

    Lines_Per_Page = SelectField(u'Lines Per Page', choices=[
                ( 10, "10"),
                ( 20, "20"),
                ( 50, "50"),
                (100, "100"),
                (  0, "All")
                ], coerce=int)

    submit = SubmitField('Clear')

