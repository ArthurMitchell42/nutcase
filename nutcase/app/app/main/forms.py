######from flask import request
# from flask_wtf import FlaskForm
# from wtforms import StringField, SelectField, SubmitField, IntegerField, BooleanField # TextAreaField
# from wtforms import SelectField, SubmitField
# from wtforms.validators import ValidationError, DataRequired, Length
######from app.models import User

# class Events_Form(FlaskForm):
#     Event_Level = SelectField(u'Level', choices=[
#                 (20,    "Info"),
#                 (30, "Warning"),
#                 (40,   "Alert"),
#                 ], 
#                 # default=('alert', "Alert")
#                 coerce=int
#                 )
#     Lines_Per_Page = SelectField(u'Lines Per Page', choices=[
#                 ( 10, "10"),
#                 ( 20, "20"),
#                 ( 50, "50"),
#                 (100, "100"),
#                 (  0, "All")
#                 ], coerce=int)
# #     update_interval = IntegerField('Update Interval')
# #     retry_interval  = IntegerField('Retry On Error')
# #     startup_delay   = IntegerField('Startup Delay')
# #     interzone_delay = IntegerField('Inter-zone Delay')
# #     ttl_value       = IntegerField('TTL')
# #     webhook_alive   = StringField('Alive Webhook')
# #     webhook_alert   = StringField('Alert Webhook')
# #     en_alive_wh     = BooleanField('Enable Alive Webhook')
# #     en_alert_wh     = BooleanField('Enable Alert Webhook')
#     submit = SubmitField('Clear')

# class DDNS_Records_Form(FlaskForm):
#     zone_name   = StringField('Zone Name')
#     record_name = StringField('Record Name')
#     submit      = SubmitField('Submit')
