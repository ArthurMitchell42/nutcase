from app import db
import arrow

from app.models import LogEntry, Log_Level
from sqlalchemy import and_, or_, true

# ===================================================================================
# Event table prototype HTML
# ===================================================================================
Table_Header = """
    <thead>
      <tr>
        <th scope="col" class="text-success text-center" style="width: 5.0%;">
        <i class="bi bi-question-circle"></i></th>
        <th scope="col" style="width: 20.0%;padding-right: 10px;">Title</th>
        <th scope="col" style="width: 5.0%;padding-right: 10px;">Category</th>
        <th scope="col" style="width: 50%;padding-right: 10px;">Details</th>
        <th scope="col" style="padding-right: 10px;">Count</th>
        <th scope="col" class="text-nowrap" style="padding-right: 15px;">First Time</th>
        <th scope="col" class="text-nowrap" style="padding-right: 15px;">Last Time</th>
        <th scope="col" style="padding-right: 10px;">Server</th>
        <th scope="col" style="padding-right: 10px;">Device</th>
      </tr>
    </thead>
    <tbody>
"""

Table_Row = """
<tr>
    <th scope="row" class="text-center {textclass} {level_class}">{level}</th>
    <td class="{textclass} text-nowrap">{title}</td>
    <td class="{textclass}">{cat}</td>
    <td class="{textclass} text-nowrap">{desc}</td>
    <td class="{textclass} text-center">{cnt}</td>
    <td class="{textclass} text-nowrap" style="padding-right: 15px;">{firsttime}</td>
    <td class="{textclass} text-nowrap" style="padding-right: 15px;">{lasttime}</td>
    <td class="{textclass} text-nowrap">{server}</td>
    <td class="{textclass} text-nowrap">{device}</td>
</tr>
"""

Level_Icons = ['<i class="bi bi-question-circle"></i>',
               '<i class="bi bi-check-circle"></i>',
               '<i class="bi bi-exclamation-circle"></i>',
               '<i class="bi bi-x-circle"></i>']

Level_Style = ['text-success', 'text-primary', 'text-warning', 'text-danger']

# ===================================================================================
# Make_Event_Table
# ===================================================================================
def Make_Event_Table(Events, Page, Lines_PP):
    Table = Table_Header

    if len(Events) == 0:
        Table += Table_Row.format(
                level_class = Level_Style[0],
                level       = Level_Icons[0],
                title       = '',
                cat         = '',
                desc        = 'No events to show',
                cnt         = '',
                firsttime   = '-',
                lasttime    = '-',
                server      = '-',
                device      = '-',
                textclass   = ''
        )
        Table += "</tbody>"
        return Table

    Start_Point = (Page - 1) * Lines_PP
    if Lines_PP == 0:
        End_Point = len(Events) - 1
    else:
        End_Point = Start_Point + (Lines_PP - 1)

    if End_Point >= len(Events):
        End_Point = len(Events) - 1

    for i in range(Start_Point, End_Point + 1):
        Event = Events[i]

        time_first = arrow.get(Event.time_first).humanize(arrow.utcnow(),
                                                          only_distance=True) + " ago"
        if time_first == 'instantly ago':
            time_first = 'Now'

        time_latest = arrow.get(Event.time_latest).humanize(arrow.utcnow(),
                                                            only_distance=True) + " ago"
        if time_latest == 'instantly ago':
            time_latest = 'Now'

        if Event.read:
            textclass = "fw-light"
        else:
            textclass = "fw-bold"

        Table += Table_Row.format(
                        level_class = Level_Style[Event.level],
                        level       = Level_Icons[Event.level],
                        title       = Event.title,
                        cat         = Event.category,
                        desc        = Event.detail,
                        cnt         = Event.occurrences,
                        firsttime   = time_first,
                        lasttime    = time_latest,
                        server      = Event.server,
                        device      = Event.device,
                        textclass   = textclass
                        )

    Table += "</tbody>"
    return Table

# ===================================================================================
# Make_Pagination
# ===================================================================================
Pag_Left_Disabled_HTML  = \
    '''<li class="page-item disabled"><a class="page-link" tabindex="-1">&laquo;</a></li>'''
Pag_Left_Enabled_HTML   = \
    '''<li class="page-item"><a class="page-link" href="./log?page={page}">&laquo;</a></li>'''
Pag_Cent_Disabled_HTML  = \
    '''<li class="page-item disabled"><a class="page-link" tabindex="-1">{page}</a></li>'''
Pag_Cent_Enabled_HTML   = \
    '''<li class="page-item"><a class="page-link" href="./log?page={page}">{page}</a></li>'''
Pag_Right_Disabled_HTML = \
    '''<li class="page-item disabled"><a class="page-link" tabindex="-1">&raquo;</a></li>'''
Pag_Right_Enabled_HTML  = \
    '''<li class="page-item"><a class="page-link" href="./log?page={page}">&raquo;</a></li>'''

def Make_Pagination(Num_Events, Lines_PP_Field, Current_Page):

    # Calculate the number of pages for the filtered results
    if isinstance(Lines_PP_Field, int):
        Lines_PP = int(Lines_PP_Field)
    else:
        Lines_PP = 10

    if Lines_PP == 0:
        Pages = 1
    else:
        Pages = int((Num_Events - 1) / Lines_PP) + 1

    if Current_Page > Pages:
        Current_Page = Pages

    Result = ''
    if Pages == 1:
        # Result = "<<d 1d >>d"
        Result += Pag_Left_Disabled_HTML + Pag_Cent_Disabled_HTML.format(page='1') \
            + Pag_Right_Disabled_HTML
    elif Pages < 6:
        if Current_Page == 1:
            Result += Pag_Left_Disabled_HTML + Pag_Cent_Disabled_HTML.format(page='1')
        else:
            Result += Pag_Left_Enabled_HTML.format(page=Current_Page - 1) \
                + Pag_Cent_Enabled_HTML.format(page='1')
        for p in range( 2, Pages + 1):
            if p == Current_Page:
                Result += Pag_Cent_Disabled_HTML.format(page=p)
            else:
                Result += Pag_Cent_Enabled_HTML.format(page=p)
        if Current_Page == Pages:
            Result += Pag_Right_Disabled_HTML
        else:
            Result += Pag_Right_Enabled_HTML.format(page=Current_Page + 1)
    elif Pages >= 6:
        if Current_Page < 4:
            if Current_Page == 1:
                Result += Pag_Left_Disabled_HTML
            else:
                Result += Pag_Left_Enabled_HTML.format(page=Current_Page - 1)
            for p in range(1, 6):
                if p == Current_Page:
                    Result += Pag_Cent_Disabled_HTML.format(page=p)
                else:
                    Result += Pag_Cent_Enabled_HTML.format(page=p)
            Result += Pag_Right_Enabled_HTML.format(page=Current_Page + 1)
        elif Current_Page >= Pages - 2:
            Result += Pag_Left_Enabled_HTML.format(page=Current_Page - 1)
            for p in range(Pages - 4, Pages + 1):
                if p == Current_Page:
                    Result += Pag_Cent_Disabled_HTML.format(page=p)
                else:
                    Result += Pag_Cent_Enabled_HTML.format(page=p)
            if Current_Page == Pages:
                Result += Pag_Right_Disabled_HTML
            else:
                Result += Pag_Right_Enabled_HTML.format(page=Current_Page + 1)
        else:
            Result += Pag_Left_Enabled_HTML.format(page=Current_Page - 1)
            for p in range(Current_Page - 2, Current_Page + 3):
                if p == Current_Page:
                    Result += Pag_Cent_Disabled_HTML.format(page=p)
                else:
                    Result += Pag_Cent_Enabled_HTML.format(page=p)
            Result += Pag_Right_Enabled_HTML.format(page=Current_Page + 1)

    return Result, Lines_PP, Current_Page

# ===================================================================================
# Get events by level and category
# ===================================================================================
def Get_Events(Level, Cat):
    Level_Filter = []
    if Level == Log_Level.alert:
        Level_Filter.append(LogEntry.level.is_(Log_Level.alert.value))
    elif Level == Log_Level.warning:
        Level_Filter.append(LogEntry.level.is_(Log_Level.alert.value))
        Level_Filter.append(LogEntry.level.is_(Log_Level.warning.value))
    elif Level == Log_Level.info:
        Level_Filter.append(LogEntry.level.is_(Log_Level.alert.value))
        Level_Filter.append(LogEntry.level.is_(Log_Level.warning.value))
        Level_Filter.append(LogEntry.level.is_(Log_Level.info.value))

    Cat_Filter = []
    if Cat:
        Cat_Filter.append(LogEntry.category.is_(Cat.value))
    else:
        Cat_Filter.append(true())

    Events = LogEntry.query.filter(
        and_(
        or_(*Level_Filter),
        or_(*Cat_Filter)
        )
    ).all()

    # Reverse list so the newest logs are on top
    Events.reverse()

    return Events

# ===================================================================================
# Mark_All_Logs_Read
# ===================================================================================
def Mark_All_Logs_Read():
    Entries = LogEntry.query.all()
    Count = 0
    for e in Entries:
        if not e.read:
            Count += 1
        e.read = True
    try:
        db.session.commit()
    except Exception:
        Count = 0
    return Count

# ===================================================================================
# Clear_All_Logs
# ===================================================================================
def Clear_All_Logs():
    Count = LogEntry.query.delete()
    try:
        db.session.commit()
    except Exception:
        Count = 0
    return Count

# ===================================================================================
# Get_Events_Table Build from functions here
# ===================================================================================
def Get_Events_Table(Level, Cat, Lines_Per_Page, Current_Page):
    Events = Get_Events(Level, Cat)
    Pagination_Block, Lines_PP, Current_Page = \
            Make_Pagination(len(Events), Lines_Per_Page, Current_Page)
    Events_Table = Make_Event_Table(Events, Current_Page, Lines_PP)

    return Pagination_Block, Events_Table
