from flask import current_app, render_template, request, flash, session
from markupsafe import Markup       # For building tables

from app.events import bp

from app.events import log_utils
from app.events.forms import Events_Form

# ===================================================================================
# Serve the end-point /events/log
# ===================================================================================
Event_List = [
    # { 'level': 20, 'title': 'A title1', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title2', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title3', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title4', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title5', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title6', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title7', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title8', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title9', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title10', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title11', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title12', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title13', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title14', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title15', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title16', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title17', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title18', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title19', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title20', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title21', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title22', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title23', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title24', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title25', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title26', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title27', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title28', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title29', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title30', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title31', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title32', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title33', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title34', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title35', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title36', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title37', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title38', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title39', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title40', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title41', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title42', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title43', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title44', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title45', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title46', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title47', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title48', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title49', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title50', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 20, 'title': 'A title51', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 30, 'title': 'A title1', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 30, 'title': 'A title2', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 30, 'title': 'A title3', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 30, 'title': 'A title4', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 30, 'title': 'A title5', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 30, 'title': 'A title6', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 30, 'title': 'A title7', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 30, 'title': 'A title8', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 30, 'title': 'A title9', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 30, 'title': 'A title10', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 30, 'title': 'A title11', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 30, 'title': 'A title12', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 30, 'title': 'A title13', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 40, 'title': 'A title1', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 40, 'title': 'A title2', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 40, 'title': 'A title3', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 40, 'title': 'A title4', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 40, 'title': 'A title5', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 40, 'title': 'A title6', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 40, 'title': 'A title7', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 40, 'title': 'A title8', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 40, 'title': 'A title9', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 40, 'title': 'A title10', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
    # { 'level': 40, 'title': 'A title11', 'desc': 'A description', 'time': '2024-01-16_18:09:30' },
]

@bp.route('/log', methods=['GET', 'POST'])
def route_events_log():
    form = Events_Form(request.form)

    # Get query from request
    Current_Page = int(request.args.get("page", 1))
    current_app.logger.debug("form.Event_Level.data {} - form.Lines_Per_Page.data {}".format(
        form.Event_Level.data, form.Lines_Per_Page.data))

    if form.is_submitted():
        action_returned = request.form["action"]
        current_app.logger.debug("action_returned {}".format(action_returned))
        # ==================================================
        if action_returned == "clear":
            current_app.logger.debug("Clear events")
            # flash('Cleared events', "text-white bg-success")
        elif action_returned == "reset":
            current_app.logger.debug("Mark all read")
            current_app.config['APP_STATUS_FLAGS']['info']    = 0
            current_app.config['APP_STATUS_FLAGS']['warning'] = 0
            current_app.config['APP_STATUS_FLAGS']['alert']   = 0
            flash('Marked all events as read', "text-white bg-success")
        elif action_returned == "redraw":
            current_app.logger.debug("Redraw")
            session['lpp'] = form.Lines_Per_Page.data
            session['level'] = form.Event_Level.data

    if 'lpp' in session:
        form.Lines_Per_Page.data = session['lpp']
    if 'level' in session:
        form.Event_Level.data = session['level']

    Events = log_utils.Filter_Events(Event_List, form.Event_Level.data)
    Pagination_Block, Lines_PP, Current_Page = \
        log_utils.Make_Pagination(len(Events), form.Lines_Per_Page.data, Current_Page)
    Events_Table = log_utils.Make_Event_Table(Events, Current_Page, Lines_PP)

    return render_template('events/events_log.html',
                            title="Events",
                            form=form,
                            pagination_block=Markup(Pagination_Block),
                            event_table=Markup(Events_Table)
                            )
