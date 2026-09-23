import os
import sqlite3

import click
from flask import current_app, g


def get_db():
    """Open a database connection (once per request) and return it."""
    # g is a place to store things for the current request only.
    if "db" not in g:
        db_path = os.path.join(current_app.instance_path, "tracker.db")
        g.db = sqlite3.connect(db_path)
        # Let us read columns by name, like row["company"], instead of row[1].
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Close the connection when the request is finished."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the tables by running schema.sql."""
    os.makedirs(current_app.instance_path, exist_ok=True)
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))


@click.command("init-db")
def init_db_command():
    """Terminal command: flask --app app init-db"""
    init_db()
    click.echo("Database created (any old data was erased).")


def init_app(app):
    """Connect the functions above to the Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
