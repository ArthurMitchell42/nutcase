import os
import logging
from logging.handlers import RotatingFileHandler #, SMTPHandler

RF_Handler_Name = "rfh"
Console_Handler_Name = "con"
Level_List = [ 'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'DEBUGV', 'DEBUGVV' ]

#==================================================================================================
# Check_Level
#==================================================================================================
def Check_Level( Level ):
    if Level in Level_List:
        return True
    return False

#==================================================================================================
# Set_Log_Level
#==================================================================================================
def Set_Log_Level( app, Level, Handler_Name=None ):
    app.logger.info("Set_Log_Level: Handler_Name {} Level {}".format( Handler_Name, Level ))

    if not Handler_Name:
        for Handler in app.logger.handlers:
            Handler.setLevel( Level )
    else:
        if Handler := Get_Handler( app, Handler_Name ):
            Handler.setLevel( Level )
    return

#==================================================================================================
# Get_RFHandler
#==================================================================================================
def Get_Handler( app, Name ):
    for Handler in app.logger.handlers:
        app.logger.debug("Handler: type {} name {}".format( type(Handler), Handler.name ))
        if (Handler.name == Name) or (Handler.name == None and Name == Console_Handler_Name):
            app.logger.debug("Found handler")
            return Handler
    app.logger.debug("Couldn't find handler")
    return None

#==================================================================================================
# Add_RF_Handler
#==================================================================================================
def Add_RF_Handler( app ):
    Logfile_Fullname = os.path.join(app.config['CONFIG_PATH'], app.config['LOGFILE_SUBPATH'], app.config['LOGFILE_NAME'])

    Logfile_Handler = RotatingFileHandler(Logfile_Fullname, maxBytes=app.config['LOGFILE_MAXBYTES'], backupCount=app.config['LOGFILE_BACKUPCOUNT'])
    Logfile_Handler.setFormatter(logging.Formatter(app.config['LOGFILE_FORMAT']))
    Logfile_Handler.name = RF_Handler_Name
    app.logger.addHandler(Logfile_Handler)
    app.logger.debug("RF handler added")
    app.logger.debug("Setting RLHandler parameters: maxBytes {} backupCount {}".format( app.config['LOGFILE_MAXBYTES'], app.config['LOGFILE_BACKUPCOUNT'] ))
    return Logfile_Handler

#==================================================================================================
# Update_RF_Handler
#==================================================================================================
def Update_RF_Handler( app ):
    app.logger.debug("In Update_RF_Handler")
    
    if Handler := Get_Handler( app, RF_Handler_Name ):
        app.logger.removeHandler(Handler)
        Add_RF_Handler( app )
    return

#==================================================================================================
# Add_Logging_Levels
#==================================================================================================
def Add_Logging_Levels():
    DEBUGV_LEVEL_NUM  = 9 
    DEBUGVV_LEVEL_NUM = 8 

    logging.addLevelName(DEBUGV_LEVEL_NUM,  "DEBUGV")
    logging.addLevelName(DEBUGVV_LEVEL_NUM, "DEBUGVV")

    def debugv(self, message, *args, **kws):
        if self.isEnabledFor(DEBUGV_LEVEL_NUM):
            self._log(DEBUGV_LEVEL_NUM, message, args, **kws) 

    def debugvv(self, message, *args, **kws):
        if self.isEnabledFor(DEBUGVV_LEVEL_NUM):
            self._log(DEBUGVV_LEVEL_NUM, message, args, **kws) 

    logging.Logger.debugv  = debugv
    logging.Logger.debugvv = debugvv
    return

    #====================================================================================
    # Set up email for the application log
    #====================================================================================
    # if not app.debug and not app.testing:
    #     if app.config['MAIL_SERVER']:
    #         auth = None
    #         if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
    #             auth = (app.config['MAIL_USERNAME'],
    #                     app.config['MAIL_PASSWORD'])
    #         secure = None
    #         if app.config['MAIL_USE_TLS']:
    #             secure = ()
    #         mail_handler = SMTPHandler(
    #             mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
    #             fromaddr='no-reply@' + app.config['MAIL_SERVER'],
    #             toaddrs=app.config['MAIL_DEFAULT_SENDER'], subject=app.config['MAIL_DEFAULT_SUBJECT'] + " " + 'App Failure',
    #             credentials=auth, secure=secure)
    #         mail_handler.setLevel(logging.ERROR)
    #         app.logger.addHandler(mail_handler)