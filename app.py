"""
Module Name: Web Application Routes
Description: This module defines the routes and associated functionalities for the web application.
"""

# ==============================
#         IMPORTS
# ==============================

import os
import logging
import pandas as pd
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    session,
)
from werkzeug.utils import secure_filename
from datetime import datetime
from dotenv import load_dotenv
from forms import UploadForm
from utils.dataLoadFunction import process_engagement_data
from utils.database import load_data_to_db

# ==============================
#         CONFIGURATION
# ==============================

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["UPLOAD_FOLDER"] = "./data/uploads"
app.config["LOG_FOLDER"] = "logs"

# Create necessary directories if they don't exist
if not os.path.exists("uploads"):
    os.makedirs("uploads")

if not os.path.exists("logs"):
    os.makedirs("logs")

# Configure logging
logging.basicConfig(
    filename=os.path.join(app.config["LOG_FOLDER"], "app.log"), level=logging.INFO
)

static_service_lines = ["All", "CBS & Elim", "Assurance", "Consulting", "Tax", "SaT"]

# ==============================
#         ROUTES
# ==============================

# ======== HOME ========


@app.route("/")
def home():
    """
    Route to handle the home page.

    Returns:
        Rendered HTML template for the home page.
    """
    return render_template("home.html")


# ======== UPLOAD ========


@app.route("/upload", methods=["GET", "POST"])
def upload():
    """
    Route to handle file uploads.

    Methods:
        GET: Renders the upload page.
        POST: Processes the uploaded file and shows a preview.

    Returns:
        Rendered HTML template for the upload page or redirect.
    """
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{timestamp}_{filename}")

        file.save(file_path)

        try:
            flash(
                "File uploaded successfully. Previewing the first 20 rows.", "success"
            )
            # Show preview of first 20 rows
            df_upload = pd.read_excel(file_path)
            df_preview = df_upload.head(20)
            session["file_path"] = file_path
            session["upload_timestamp"] = timestamp
            return render_template(
                "upload.html",
                form=form,
                table=df_preview.style.set_table_attributes(
                    'table_id="previewTable" class="table table-striped"'
                ),
            )
        except Exception as e:
            flash(f"Error processing data: {str(e)}", "danger")
            return redirect(url_for("upload"))

    return render_template("upload.html", form=form)


# ======== DOWNLOAD ========


@app.route("/download/<filename>")
def download(filename):
    """
    Route to handle file downloads.

    Args:
        filename (str): The name of the file to download.

    Returns:
        The file as an attachment.
    """
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    return send_file(file_path, as_attachment=True)


@app.route("/download_log/<filename>")
def download_log(filename):
    """
    Route to handle log file downloads.

    Args:
        filename (str): The name of the log file to download.

    Returns:
        The log file as an attachment.
    """
    file_path = os.path.join(app.config["LOG_FOLDER"], filename)
    return send_file(file_path, as_attachment=True)


# ======== DELEGATES ========


@app.route("/delegates")
def delegates():
    """
    Route to handle the delegates page.

    Returns:
        Rendered HTML template for the delegates page.
    """
    return render_template("delegates.html")


# ======== APPLY ========


@app.route("/etc_exception_application")
def etc_exception_application():
    """
    Route to handle the ETC exception application page.

    Returns:
        Rendered HTML template for the ETC exception application page.
    """
    return render_template("etc_exception_application.html")


# ======== APPROVAL ========


@app.route("/ep_approval")
def ep_approval():
    """
    Route to handle the EP approval page.

    Returns:
        Rendered HTML template for the EP approval page.
    """
    return render_template("ep_approval.html")


@app.route("/finance_approval")
def finance_approval():
    """
    Route to handle the finance approval page.

    Returns:
        Rendered HTML template for the finance approval page.
    """
    return render_template("finance_approval.html")


# ======== REPORTS ========


@app.route("/reports")
def reports():
    """
    Route to handle the reports page.

    Returns:
        Rendered HTML template for the reports page.
    """
    return render_template("reports.html")


# ======== ERROR HANDLING ========


@app.errorhandler(404)
def page_not_found(e):
    """
    Route to handle 404 errors.

    Args:
        e: The error.

    Returns:
        Rendered HTML template for the 404 error page.
    """
    return render_template("404.html"), 404


# ==============================
#         MAIN
# ==============================

if __name__ == "__main__":
    app.run(debug=True)
