from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField

class Events_Form(FlaskForm):
    Event_Level = SelectField(u'Level', choices=[
                (1,    "Info"),
                (2, "Warning"),
                (3,   "Alert"),
                ],
                default=(1, "Info"),
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
