#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template
from waitress import serve

app = Flask(__name__, static_url_path="/static", static_folder="static")


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
        The rendered template of the data page
    """
    return render_template("data.html")


@app.route("/data-privacy")
def data_privacy() -> str:
    """
    Register the controller for the data page.

    Returns
    -------
    str
        The rendered template of the data-privacy statement
    """
    return render_template("data-privacy.html")


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


@app.route("/maintenance")
def maintenance() -> str:
    """
    Register the controller for the maintenance page.

    Returns
    -------
    str
        The rendered template of the maintenance page
    """
    # Website to ping for information
    scc_website = "https://www.scc.kit.edu/en/services/announcements.php"

    # Message to print
    message = f"The following information regarding possible causes for this error have been found via {scc_website}: <br>"
    try:
        # Fetch the page.
        response = requests.get(scc_website)
        response.raise_for_status()  # Raise HTTPError for bad responses
        html = response.text
    except requests.RequestException:
        message = (
            f"Unfortunately, the website providing information on current errors ({scc_website}) could not be "
            f"accessed. \n Therefore, we can provide no further information regarding the error at this time."
        )
    else:
        try:
            # Parse the HTML.
            b = BeautifulSoup(html, "html.parser")

            # Locate and filter the relevant announcements.
            lsdf_messages = [
                e.text for e in b.find_all("h2", class_="meldung") if "LSDF" in e.text
            ]

            # Add messages to the output.
            if lsdf_messages:
                message += "<br>".join(f"- {error}." for error in lsdf_messages)
            else:
                message = (
                    f"According to the website providing information on current errors ({scc_website}), there are no "
                    f"current issues. We are sorry we cannot automatically provide you with further information - we "
                    f"are working to fix this issue as soon as possible."
                )
        except Exception:
            message = (
                "Unfortunately there was an error in the service that automatically looks for possible errors. We are "
                "sorry we cannot automatically provide you with further information - we are working to fix this "
                "issue as soon as possible."
            )
    return render_template("maintenance.html", message=message)


if __name__ == "__main__":
    serve(app, host="127.0.0.1", port=8000)
