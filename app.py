from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
import os
import pandas as pd
from forms import UploadForm
from dataLoadFunction import process_engagement_data
import logging

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


@app.route("/", methods=["GET", "POST"])
def index():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        file.save(file_path)

        try:
            flash(
                "File uploaded successfully. Previewing the first 20 rows.", "success"
            )
            # Show preview of first 20 rows
            df_preview = pd.read_excel(file_path).head(20)
            return render_template(
                "index.html",
                form=form,
                table=df_preview.to_html(classes="table table-striped"),
                file_path=file_path,
            )
        except Exception as e:
            flash(f"Error processing file: {str(e)}", "danger")
            return redirect(url_for("index"))

    return render_template("index.html", form=form)


@app.route("/process", methods=["POST"])
def process():
    file_path = request.form["file_path"]
    start_row = int(request.form["start_row"])
    service_line = request.form["service_line"]
    export_log = "export_log" in request.form

    try:
        flash("Processing data...", "info")
        # Process the data
        df_processed = process_engagement_data(
            file_path, start_row=start_row, service_line=service_line
        )
        flash("Data processed successfully.", "success")

        # Save processed data to a new Excel file
        processed_file_path = os.path.join(
            app.config["UPLOAD_FOLDER"], "processed_data.xlsx"
        )
        df_processed.to_excel(processed_file_path, index=False)

        # Limit displayed rows to 20
        df_display = df_processed.head(20)

        if export_log:
            return render_template(
                "processed.html",
                table=df_display.to_html(classes="table table-striped"),
                download_link=processed_file_path,
                log_link=url_for("download_log"),
            )
        else:
            return render_template(
                "processed.html",
                table=df_display.to_html(classes="table table-striped"),
                download_link=processed_file_path,
            )

    except Exception as e:
        flash(f"Error processing data: {str(e)}", "danger")
        return redirect(url_for("index"))


@app.route("/download_log")
def download_log():
    log_file_path = os.path.join(app.config["LOG_FOLDER"], "app.log")
    return send_file(log_file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
