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
from dataLoadFunction import process_engagement_data
from database_utils import load_data_to_db

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["LOG_FOLDER"] = "logs"

if not os.path.exists("uploads"):
    os.makedirs("uploads")

if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename=os.path.join(app.config["LOG_FOLDER"], "app.log"), level=logging.INFO
)

static_service_lines = ["All", "CBS & Elim", "Assurance", "Consulting", "Tax", "SaT"]


@app.route("/")
def home():
    return render_template("home.html")


############ UPLOAD ############


@app.route("/upload", methods=["GET", "POST"])
def upload():
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
                    'table_id="previewTable" classes="table table-striped table-sm" data-toggle="table" data-pagination="true" data-search="true"'
                ).to_html(),
                file_path=file_path,
                service_lines=static_service_lines,
                size_preview=df_upload.shape[0],
            )
        except Exception as e:
            flash(f"Error processing file: {str(e)}", "danger")
            return redirect(url_for("upload"))

    return render_template("upload.html", form=form, service_lines=static_service_lines)


############ PROCESS ############


@app.route("/process", methods=["POST"])
def process():
    file_path = session.get("file_path")
    start_row = int(request.form["start_row"])
    service_line = request.form["service_line"]
    export_log = "export_log" in request.form
    upload_timestamp = session.get("upload_timestamp")
    upload_user = (
        request.remote_addr
    )  # For simplicity, using the remote address as the user

    try:
        # Process the data
        df_processed = process_engagement_data(
            file_path, start_row=start_row, service_line=service_line
        )

        upload_display_size = df_processed.shape[0]

        # Save processed data to a new Excel file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        processed_file_name = f"processed_data_{timestamp}.xlsx"
        processed_file_path = os.path.join(
            app.config["UPLOAD_FOLDER"], processed_file_name
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
            )
        else:
            return render_template(
                "processed.html",
                table=df_display,
                download_link=processed_file_name,
                size_process=upload_display_size,
            )

    except Exception as e:
        flash(f"Error processing data: {str(e)}", "danger")
        return redirect(url_for("upload"))


@app.route("/download/<filename>")
def download(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    return send_file(file_path, as_attachment=True)


@app.route("/download_log/<filename>")
def download_log(filename):
    file_path = os.path.join(app.config["LOG_FOLDER"], filename)
    return send_file(file_path, as_attachment=True)


############ DELEGATES ############


@app.route("/delegates")
def delegates():
    return render_template("delegates.html")


@app.route("/etc_exception_application")
def etc_exception_application():
    return render_template("etc_exception_application.html")


@app.route("/ep_approval")
def ep_approval():
    return render_template("ep_approval.html")


@app.route("/finance_approval")
def finance_approval():
    return render_template("finance_approval.html")


@app.route("/reports")
def reports():
    return render_template("reports.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
