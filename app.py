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
from forms import LoadForm
from utils.dataLoadFunction import process_engagement_data
from utils.database import load_data_to_db

# ==============================
#         CONFIGURATION
# ==============================
# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = "your_secret_key"
LOAD_FOLDER = "./data/loading"
LOG_FOLDER = "./logs"
app.config["LOAD_FOLDER"] = LOAD_FOLDER
app.config["LOG_FOLDER"] = LOG_FOLDER

if not os.path.exists(LOAD_FOLDER):
    os.makedirs(LOAD_FOLDER)

if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

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
    return render_template("home.html")


# ======== LOAD ========
@app.route("/load", methods=["GET", "POST"])
def load():
    form = LoadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(app.config["LOAD_FOLDER"], f"{timestamp}_{filename}")

        file.save(file_path)

        try:
            flash("File loaded successfully. Previewing the first 20 rows.", "success")
            # Show preview of first 20 rows
            df_load = pd.read_excel(file_path)
            df_preview = df_load.head(20)
            session["file_path"] = file_path
            session["load_timestamp"] = timestamp
            return render_template(
                "load.html",
                form=form,
                table=df_preview.style.set_table_attributes(
                    'table_id="previewTable" classes="table table-striped table-sm" data-toggle="table" data-pagination="true" data-search="true"'
                ).to_html(),
                file_path=file_path,
                service_lines=static_service_lines,
            )
        except Exception as e:
            flash(f"Error processing file: {str(e)}", "danger")
            return redirect(url_for("load"))

    return render_template("load.html", form=form, service_lines=static_service_lines)
    # TODO: #8 Add count for number of rows in the preview file


# ======== PROCESS ========
@app.route("/process", methods=["POST"])
def process():
    file_path = session.get("file_path")
    start_row = int(request.form["start_row"])
    service_line = request.form["service_line"]
    export_log = "export_log" in request.form
    upload_timestamp = session.get("load_timestamp")
    upload_user = (
        request.remote_addr
    )  # For simplicity, using the remote address as the user

    try:
        # Process the data
        df_processed = process_engagement_data(
            file_path, start_row=start_row, service_line=service_line
        )

        df_procesed_size = df_processed.shape[0]

        # Save processed data to a new Excel file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        processed_file_name = f"processed_data_{timestamp}.xlsx"
        processed_file_path = os.path.join(
            app.config["LOAD_FOLDER"], processed_file_name
        )
        df_processed.to_excel(processed_file_path, index=False)

        # Load data to database
        load_data_to_db(df_processed, "engagement_data", upload_timestamp, upload_user)

        # Limit displayed rows to 20
        df_display = (
            df_processed.head(20)
            .style.set_table_attributes(
                'table_id="processedTable" classes="table table-striped table-sm" data-toggle="table" data-pagination="true" data-search="true"'
            )
            .to_html()
        )

        flash("Data processed successfully.", "success")

        if export_log:
            log_file_name = f"app_{timestamp}.log"
            logging.shutdown()
            os.rename(
                os.path.join(app.config["LOG_FOLDER"], "app.log"),
                os.path.join(app.config["LOG_FOLDER"], log_file_name),
            )
            return render_template(
                "processed.html",
                table=df_display,
                download_link=processed_file_name,
                log_link=log_file_name,
                size=df_procesed_size,
            )
        else:
            return render_template(
                "processed.html",
                table=df_display,
                download_link=processed_file_name,
                size=df_procesed_size,
            )

    except Exception as e:
        flash(f"Error processing data: {str(e)}", "danger")
        return redirect(url_for("load"))


# ======== DOWNLOADS ========
@app.route("/download/<filename>")
def download(filename):
    file_path = os.path.join(app.config["LOAD_FOLDER"], filename)
    return send_file(file_path, as_attachment=True)


@app.route("/download_log/<filename>")
def download_log(filename):
    file_path = os.path.join(app.config["LOG_FOLDER"], filename)
    return send_file(file_path, as_attachment=True)


# ======== DELEGATES ========
@app.route("/delegates")
def delegates():
    return render_template("delegates.html")


# ======== APPLICATION ========
@app.route("/etc_exception_application")
def etc_exception_application():
    return render_template("etc_exception_application.html")


# ======== EP APPROVAL ========
@app.route("/ep_approval")
def ep_approval():
    return render_template("ep_approval.html")


# ======== FINANCE APPROVAL ========
@app.route("/finance_approval")
def finance_approval():
    return render_template("finance_approval.html")


# ======== REPORTS ========
@app.route("/reports")
def reports():
    return render_template("reports.html")


# ======== 404 ========
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
