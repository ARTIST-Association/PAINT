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
    return render_template("home.html")


@app.route("/data")
def data() -> str:
    """
    Register the controller for the data page.

    Returns
    -------
    str
        The rendered template of the main landing page
    """
    return render_template("data.html")


@app.route("/papers")
def papers() -> str:
    """
    Register the controller for the papers page.

    Returns
    -------
    str
        The rendered template of the main landing page
    """
    return render_template("papers.html")


@app.route("/partners")
def partners() -> str:
    """
    Register the controller for the partners page.

    Returns
    -------
    str
        The rendered template of the main landing page
    """
    return render_template("partners.html")


@app.route("/resources")
def resources() -> str:
    """
    Register the controller for the resources page.

    Returns
    -------
    str
        The rendered template of the main landing page
    """
    return render_template("resources.html")


if __name__ == "__main__":
    app.run()
