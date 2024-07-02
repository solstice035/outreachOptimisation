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
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

matplotlib.use("Agg")

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
            df_load = pd.read_excel(file_path)
            df_preview = df_load.head(20)

            # Calculate counts
            engagement_status_counts = df_load["Engagement Status"].value_counts()

            # Filter the DataFrame for Engagement Status = "Released"
            df_filtered = df_load[df_load["Engagement Status"] == "Released"]
            service_line_counts = df_filtered[
                "Engagement Partner Service Line"
            ].value_counts()

            # Set Seaborn style
            sns.set(style="white")

            # Create charts
            def create_bar_chart(data, x_label):
                plt.figure(figsize=(10, 6))
                ax = sns.barplot(
                    x=data.values, y=data.index, palette="viridis", hue=data.index
                )
                ax.set(
                    xlabel=x_label, ylabel=None
                )  # Remove y-axis label, keep x-axis label
                ax.set_title("")

                # Add data labels
                for index, value in enumerate(data.values):
                    ax.text(value, index, str(value), color="black", ha="left")

                sns.despine(left=True, bottom=True)  # Remove borders
                img = io.BytesIO()
                plt.savefig(
                    img, format="png", bbox_inches="tight"
                )  # bbox_inches='tight' removes extra borders
                plt.close()
                img.seek(0)
                return base64.b64encode(img.getvalue()).decode()

            chart1_url = create_bar_chart(engagement_status_counts, "Count")
            chart2_url = create_bar_chart(service_line_counts, "Count")

            session["file_path"] = file_path
            session["load_timestamp"] = timestamp

            return render_template(
                "load.html",
                form=form,
                table=df_preview.style.set_table_attributes(
                    'table_id="previewTable" classes="table table-striped table-sm" data-toggle="table" data-pagination="true" data-search="true" data-page-size="5"'
                ).to_html(),
                file_path=file_path,
                service_lines=static_service_lines,
                chart1_url=chart1_url,
                chart2_url=chart2_url,
            )
        except Exception as e:
            flash(f"Error processing file: {str(e)}", "danger")
            return redirect(url_for("load"))

    return render_template("load.html", form=form, service_lines=static_service_lines)

    # TODO: #8 Add count for number of rows in the preview file
    # TODO: #12 Add stats for the file, split by service line and by status


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


# ======== INDEX ========
@app.route("/")
def index():
    return render_template("index.html")


# ======== 404 ========
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    # Run the plotting script to generate the plot
    os.system("python plot.py")
    app.run(debug=True)
