# date and timedelta are built into Python. We use them to check date
# formats and to work out which deadlines are coming up soon.
from datetime import date, timedelta

# Import the Flask class from the Flask library we installed.
# render_template fills in an HTML file from the templates/ folder.
# request holds the data the browser sent (like form fields).
# redirect and url_for send the browser to another page.
# abort stops the request with an error page (like 404 Not Found).
from flask import Flask, abort, redirect, render_template, request, url_for

# Our own database helpers, from db.py.
import db

# Create the web app. __name__ tells Flask where this file lives,
# so it can find other project folders (like templates/) later.
app = Flask(__name__)

# Hook up the database: closes connections and adds the init-db command.
db.init_app(app)

# The only statuses allowed. Must match the CHECK rule in schema.sql.
STATUSES = ["interested", "applied", "interviewing", "offer", "rejected"]

# Every form field, in the same order as the database columns.
FIELDS = ["company", "role", "location", "date_applied", "deadline",
          "posting_url", "status", "notes"]


def read_form():
    """Get each field from the submitted form, with extra spaces removed."""
    return {field: request.form.get(field, "").strip() for field in FIELDS}


def validate(form):
    """Return a list of error messages. An empty list means the form is OK."""
    errors = []
    if not form["company"]:
        errors.append("Company is required.")
    if not form["role"]:
        errors.append("Role is required.")
    if form["status"] not in STATUSES:
        errors.append("Please choose a valid status.")
    for field, label in [("date_applied", "Date applied"), ("deadline", "Deadline")]:
        if form[field]:
            try:
                date.fromisoformat(form[field])
            except ValueError:
                errors.append(f"{label} must be a date like 2026-09-23.")
    if form["posting_url"] and not form["posting_url"].startswith(("http://", "https://")):
        errors.append("Posting link must start with http:// or https://")
    return errors


# Columns you can sort by, and the heading shown for each.
# Only names in this list are ever put into the SQL (see index()).
SORTABLE = {
    "company": "Company",
    "role": "Role",
    "location": "Location",
    "status": "Status",
    "date_applied": "Date applied",
    "deadline": "Deadline",
}


# Home page: show applications, optionally filtered by status and sorted.
# Example URL: /?status=applied&sort=deadline&order=asc
@app.route("/")
def index():
    status = request.args.get("status", "")
    sort = request.args.get("sort", "")
    order = request.args.get("order", "asc")

    sql = "SELECT * FROM applications"
    params = []
    if status in STATUSES:
        sql += " WHERE status = ?"
        params.append(status)
    else:
        status = ""  # Ignore unknown statuses and show everything.

    if sort in SORTABLE:
        direction = "DESC" if order == "desc" else "ASC"
        # Column names can't use ? placeholders, so we only allow names from
        # SORTABLE. "IS NULL" puts blank cells last in both directions.
        sql += f" ORDER BY {sort} IS NULL, {sort} COLLATE NOCASE {direction}"
    else:
        sort = ""
        # Default: newest first. id breaks ties when added in the same second.
        sql += " ORDER BY created_at DESC, id DESC"

    database = db.get_db()
    applications = database.execute(sql, params).fetchall()

    # Summary counts for ALL applications (not just the filtered ones).
    # GROUP BY gives one row per status, e.g. ("applied", 3).
    rows = database.execute(
        "SELECT status, COUNT(*) FROM applications GROUP BY status"
    ).fetchall()
    counts = {s: 0 for s in STATUSES}
    for row in rows:
        counts[row[0]] = row[1]

    # Dates are stored as YYYY-MM-DD text, which compares correctly as text,
    # so the template can check things like: deadline <= soon.
    today = date.today()
    return render_template("index.html", applications=applications,
                           statuses=STATUSES, columns=SORTABLE,
                           status=status, sort=sort, order=order,
                           counts=counts, total=sum(counts.values()),
                           today=today.isoformat(),
                           soon=(today + timedelta(days=7)).isoformat())


def get_application(app_id):
    """Find one application by id, or show a 404 "Not Found" page."""
    row = db.get_db().execute(
        "SELECT * FROM applications WHERE id = ?", (app_id,)
    ).fetchone()
    if row is None:
        abort(404)
    return row


# Add page. GET shows an empty form; POST saves what was typed.
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        form = read_form()
        errors = validate(form)
        if errors:
            # Show the form again, keeping what was typed.
            return render_template("form.html", title="Add application",
                                   form=form, errors=errors, statuses=STATUSES)

        # Save blank optional fields as NULL (empty) instead of "".
        values = [form[field] or None for field in FIELDS]
        database = db.get_db()
        database.execute(
            "INSERT INTO applications (company, role, location, date_applied,"
            " deadline, posting_url, status, notes)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            values,
        )
        database.commit()
        return redirect(url_for("index"))

    # GET: an empty form, with status starting as "interested".
    empty_form = {field: "" for field in FIELDS}
    empty_form["status"] = "interested"
    return render_template("form.html", title="Add application",
                           form=empty_form, errors=[], statuses=STATUSES)


# Edit page. <int:app_id> takes the number from the URL, like /edit/3.
@app.route("/edit/<int:app_id>", methods=["GET", "POST"])
def edit(app_id):
    row = get_application(app_id)

    if request.method == "POST":
        form = read_form()
        errors = validate(form)
        if errors:
            return render_template("form.html", title="Edit application",
                                   form=form, errors=errors, statuses=STATUSES)

        values = [form[field] or None for field in FIELDS]
        database = db.get_db()
        database.execute(
            "UPDATE applications SET company = ?, role = ?, location = ?,"
            " date_applied = ?, deadline = ?, posting_url = ?, status = ?,"
            " notes = ? WHERE id = ?",
            values + [app_id],
        )
        database.commit()
        return redirect(url_for("index"))

    # GET: fill the form with the saved values (blank instead of None).
    form = {field: row[field] or "" for field in FIELDS}
    return render_template("form.html", title="Edit application",
                           form=form, errors=[], statuses=STATUSES)


# Delete. POST only, so visiting a link can never delete anything.
@app.route("/delete/<int:app_id>", methods=["POST"])
def delete(app_id):
    get_application(app_id)  # 404 if it doesn't exist.
    database = db.get_db()
    database.execute("DELETE FROM applications WHERE id = ?", (app_id,))
    database.commit()
    return redirect(url_for("index"))
