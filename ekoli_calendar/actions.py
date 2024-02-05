import re
from datetime import date, timedelta
from typing import List, Optional, Tuple, cast  # noqa: F401

from flask import abort, current_app, g, jsonify, make_response, redirect, render_template, request
from werkzeug.wrappers import Response

import ekoli_calendar.constants as constants
from ekoli_calendar.app_utils import (
    next_month_link,
    previous_month_link,
)
from ekoli_calendar.calendar_data import CalendarData
from ekoli_calendar.gregorian_calendar import GregorianCalendar


def main_calendar_action() -> Response:
    # You can get the calendar ID from the URL too, it's good to keep that option
    # But for now, calendar ID is overridden by a single calendar for everyone
    calendar_id = "ekoli_calendar"
    GregorianCalendar.setfirstweekday(current_app.config["WEEK_STARTING_DAY"])

    current_day, current_month, current_year = GregorianCalendar.current_date()
    year = int(request.args.get("y", current_year))
    year = max(min(year, current_app.config["MAX_YEAR"]), current_app.config["MIN_YEAR"])
    month = int(request.args.get("m", current_month))
    month = max(min(month, 12), 1)
    month_name = GregorianCalendar.MONTH_NAMES[month - 1]

    if current_app.config["HIDE_PAST_TASKS"]:
        view_past_tasks = False
    else:
        view_past_tasks = request.cookies.get("ViewPastTasks", "1") == "1"

    calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])
    try:
        data = calendar_data.load_calendar(calendar_id)
    except FileNotFoundError:
        abort(404)

    tasks = calendar_data.tasks_from_calendar(year, month, data)
    # tasks = calendar_data.add_repetitive_tasks_from_calendar(year, month, data, tasks)

    if not view_past_tasks:
        calendar_data.hide_past_tasks(year, month, tasks)

    if current_app.config["WEEK_STARTING_DAY"] == constants.WEEK_START_DAY_MONDAY:
        weekdays_headers = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    else:
        weekdays_headers = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]

    return cast(
        Response,
        render_template(
            "calendar.html",
            calendar_id=calendar_id,
            year=year,
            month=month,
            month_name=month_name,
            current_year=current_year,
            current_month=current_month,
            current_day=current_day,
            month_days=GregorianCalendar.month_days(year, month),
            previous_month_link=previous_month_link(year, month),
            next_month_link=next_month_link(year, month),
            base_url=current_app.config["BASE_URL"],
            tasks=tasks,
            display_view_past_button=current_app.config["SHOW_VIEW_PAST_BUTTON"],
            weekdays_headers=weekdays_headers,
        ),
    )

def hide_repetition_task_instance_action(calendar_id: str, year: str, month: str, day: str, task_id: str) -> Response:
    calendar_data = CalendarData(current_app.config["DATA_FOLDER"], current_app.config["WEEK_STARTING_DAY"])
    calendar_data.hide_repetition_task_instance(
        calendar_id=calendar_id,
        year_str=year,
        month_str=month,
        day_str=day,
        task_id_str=task_id,
    )

    return cast(Response, jsonify({}))
