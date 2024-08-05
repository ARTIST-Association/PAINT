#!/usr/bin/env python

from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home() -> str:
    """
    Register the controller for the main landing page.

    Returns
    -------
    str
        The rendered template of the main landing page
    """
    return render_template("base.html")


if __name__ == "__main__":
    app.run()
