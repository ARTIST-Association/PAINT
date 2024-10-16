#!/usr/bin/env python

from flask import Flask, render_template
from waitress import serve

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
    Register the controller for the preprocessing page.

    Returns
    -------
    str
        The rendered template of the preprocessing page
    """
    return render_template("preprocessing.html")


@app.route("/data-privacy")
def data_privacy() -> str:
    """
    Register the controller for the preprocessing page.

    Returns
    -------
    str
        The rendered template of the preprocessing-privacy statement
    """
    return render_template("preprocessing-privacy.html")


@app.route("/legal-information")
def legal_information() -> str:
    """
    Register the controller for the legal information page.

    Returns
    -------
    str
        The rendered template of the legal information
    """
    return render_template("legal-information.html")


@app.route("/papers")
def papers() -> str:
    """
    Register the controller for the papers page.

    Returns
    -------
    str
        The rendered template of the papers page
    """
    return render_template("papers.html")


@app.route("/partners")
def partners() -> str:
    """
    Register the controller for the partners page.

    Returns
    -------
    str
        The rendered template of the partners page
    """
    return render_template("partners.html")


@app.route("/resources")
def resources() -> str:
    """
    Register the controller for the resources page.

    Returns
    -------
    str
        The rendered template of the resources page
    """
    return render_template("resources.html")


if __name__ == "__main__":
    serve(app, host="127.0.0.1", port=8000)
