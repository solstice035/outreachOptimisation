from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import pandas as pd
from forms import UploadForm
from dataLoadFunction import process_engagement_data

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["UPLOAD_FOLDER"] = "uploads"

if not os.path.exists("uploads"):
    os.makedirs("uploads")


@app.route("/", methods=["GET", "POST"])
def index():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        start_row = form.start_row.data
        service_line = form.service_line.data
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        # Show preview
        df_preview = pd.read_excel(file_path).head(10)
        return render_template(
            "preview.html",
            table=df_preview.to_html(),
            file_path=file_path,
            start_row=start_row,
            service_line=service_line,
        )

    return render_template("index.html", form=form)


@app.route("/process", methods=["POST"])
def process():
    file_path = request.form["file_path"]
    start_row = int(request.form["start_row"])
    service_line = request.form["service_line"]

    try:
        df_processed = process_engagement_data(
            file_path, start_row=start_row, service_line=service_line
        )
        return render_template("preview.html", table=df_processed.to_html())
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
