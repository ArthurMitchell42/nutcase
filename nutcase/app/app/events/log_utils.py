# from flask import current_app

# ===================================================================================
# Event table prototype HTML
# ===================================================================================
Table_Header = """
    <thead>
        <tr>
        <th scope="col" style="width: 5.0%">Level</th>
        <th scope="col" style="width: 15.0%">Title</th>
        <th scope="col">Details</th>
        <th scope="col" style="width: 5.0%">Time</th>
        </tr>
    </thead>
    <tbody>
"""

Table_Row = """
<tr>
    <th scope="row" class="{level_class}">{level}</th>
    <td>{title}</td>
    <td>{desc}</td>
    <td>{time}</td>
</tr>
"""

Levels = {
    20: 'Info',
    30: 'Warning',
    40: 'Alert',
}

# ===================================================================================
# Make_Event_Table
# ===================================================================================
def Make_Event_Table(Events, Page, Lines_PP):
    Table = Table_Header

    if len(Events) == 0:
        Table += Table_Row.format(
                level       = '',
                level_class = '',
                title       = '',
                desc        = 'No events to show',
                time        = ''
        )
        Table += "</tbody>"
        return Table

    Level_Class = ''
    Start_Point = (Page - 1) * Lines_PP
    if Lines_PP == 0:
        End_Point = len(Events) - 1
    else:
        End_Point = Start_Point + (Lines_PP - 1)

    if End_Point > len(Events):
        End_Point = len(Events) - 1

    for i in range(Start_Point, End_Point + 1):
        Event = Events[i]
        Table += Table_Row.format(
                            level       = Levels[Event['level']],
                            level_class = Level_Class,
                            title       = Event['title'],
                            desc        = Event['desc'],
                            time        = Event['time']
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
# Filter events by level
# ===================================================================================
def Filter_Events(Event_List, Level):
    if Level:
        Filter_Level = int(Level)
    else:
        Filter_Level = 0

    Events = []
    for e in Event_List:
        if e['level'] >= Filter_Level:
            Events.append(e)

    return Events
