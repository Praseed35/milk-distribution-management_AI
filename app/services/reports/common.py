import csv
import io
from datetime import date, datetime, timedelta

from fastapi.responses import StreamingResponse

from app.models.employee import Employee


def resolve_date_range(
    preset: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> tuple[date, date]:
    today = date.today()

    if preset:
        if preset == "today":
            return today, today
        elif preset == "yesterday":
            yesterday = today - timedelta(days=1)
            return yesterday, yesterday
        elif preset == "this_week":
            start = today - timedelta(days=today.weekday())
            return start, today
        elif preset == "last_week":
            end = today - timedelta(days=today.weekday() + 1)
            start = end - timedelta(days=6)
            return start, end
        elif preset == "this_month":
            start = today.replace(day=1)
            return start, today
        elif preset == "last_month":
            first_of_this = today.replace(day=1)
            end = first_of_this - timedelta(days=1)
            start = end.replace(day=1)
            return start, end
        elif preset == "this_year":
            start = today.replace(month=1, day=1)
            return start, today

    if from_date and not to_date:
        return from_date, from_date

    if not from_date and not to_date:
        start = today.replace(day=1)
        return start, today

    return from_date or today, to_date or today


def get_role_restricted_routes(db, current_user, requested_route_id: int | None = None) -> int | None:
    if current_user.role == "DELIVERY_PARTNER":
        employee = (
            db.query(Employee)
            .filter(Employee.user_id == current_user.id)
            .first()
        )
        if not employee or not employee.route_id:
            return -1
        if requested_route_id is not None and requested_route_id != employee.route_id:
            return -1
        return employee.route_id
    return None


def generate_csv_response(data: list[dict], filename: str) -> StreamingResponse:
    output = io.StringIO()
    if data:
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    else:
        output.write("")
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
    )
