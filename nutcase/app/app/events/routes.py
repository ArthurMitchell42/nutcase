from flask import current_app, render_template, request, flash, session
from markupsafe import Markup

from app.events import bp

from app.events import log_utils
from app.events.forms import Events_Form

from app.models import Log_Level

# ===================================================================================
# Serve the end-point /events/log
# ===================================================================================
@bp.route('/log', methods=['GET', 'POST'])
def route_events_log():
    form = Events_Form(request.form)

    # Get query from request
    Current_Page = int(request.args.get("page", 1))

    if form.is_submitted():
        action_returned = request.form["action"]
        # ==================================================
        if action_returned == "clear":
            current_app.logger.debug("Clear events")
            Count = log_utils.Clear_All_Logs()
            flash(f'Cleared {Count} events', "text-white bg-success")
        # ==================================================
        elif action_returned == "reset":
            current_app.config['APP_STATUS_FLAGS']['info']    = 0
            current_app.config['APP_STATUS_FLAGS']['warning'] = 0
            current_app.config['APP_STATUS_FLAGS']['alert']   = 0
            Count = log_utils.Mark_All_Logs_Read()
            flash(f'Marked {Count} events as read', "text-white bg-success")
        # ==================================================
        elif action_returned == "redraw":
            session['lpp'] = form.Lines_Per_Page.data
            session['level'] = form.Event_Level.data
        # ==================================================
        elif action_returned == "refresh":
            pass

    if 'lpp' in session:
        form.Lines_Per_Page.data = session['lpp']
    if 'level' in session:
        form.Event_Level.data = session['level']

    if form.Event_Level.data is None:
        Current_Log_Level = Log_Level.info
    elif form.Event_Level.data > 0 and form.Event_Level.data < 4:
        Current_Log_Level = Log_Level(form.Event_Level.data)
    else:
        Current_Log_Level = Log_Level.info

    if form.Lines_Per_Page.data is None:
        Current_LPP = 10
    else:
        Current_LPP = form.Lines_Per_Page.data

    Pagination_Block, Events_Table = log_utils.Get_Events_Table(
        Level = Log_Level(Current_Log_Level),
        Cat = None,
        Lines_Per_Page = Current_LPP,
        Current_Page = Current_Page
    )

    return render_template('events/events_log.html',
                            title="Events",
                            form=form,
                            pagination_block=Markup(Pagination_Block),
                            event_table=Markup(Events_Table)
                            )
