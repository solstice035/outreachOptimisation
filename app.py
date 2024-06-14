# app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from utils.data_load import process_engagement_data
from utils.database import (
    load_data_to_db,
    insert_delegates,
    get_db_connection,
    is_user_authorized,
)
import logging
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"


# Home page route
@app.route("/")
def home():
    return render_template("index.html")


# Upload page route
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        if not file:
            flash("No file selected", "danger")
            return redirect(request.url)
        start_row = int(request.form.get("start_row", 0))
        service_line = request.form.get("service_line")
        # Save file and process data
        file_path = f"./data/input/{file.filename}"
        file.save(file_path)
        try:
            df = process_engagement_data(
                file_path, start_row=start_row, service_line=service_line
            )
            # Log and generate file names
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"processed_{timestamp}.xlsx"
            log_filename = f"logs/app_{timestamp}.log"
            # Save processed file
            df.to_excel(f"./data/output/{output_filename}", index=False)
            # Load data into the database
            load_data_to_db(
                df,
                "engagement_data",
                upload_timestamp=datetime.now(),
                upload_user="user_id",
            )
            flash("File processed and data loaded successfully", "success")
            return render_template(
                "processed.html",
                table=df.head(20).to_html(),
                download_link=output_filename,
                log_link=log_filename,
            )
        except Exception as e:
            logging.error(f"Error processing data: {e}")
            flash(f"Error processing data: {e}", "danger")
            return redirect(request.url)
    return render_template("index.html")


# Add delegate route
@app.route("/add_delegate", methods=["GET", "POST"])
def add_delegate():
    if request.method == "POST":
        engagement_id = request.form["engagement_id"]
        delegate_names = request.form.getlist("delegate_name[]")
        delegate_emails = request.form.getlist("delegate_email[]")
        end_dates = request.form.getlist("end_date[]")

        # Placeholder for user ID; replace with actual user authentication
        user_id = (
            "1234567"  # Example user ID; should be fetched from session/auth context
        )

        if not is_user_authorized(user_id, engagement_id):
            flash(
                "You are not authorized to add delegates to this engagement.", "danger"
            )
            return redirect(url_for("add_delegate"))

        try:
            connection = get_db_connection()
            insert_delegates(
                connection,
                engagement_id,
                delegate_names,
                delegate_emails,
                end_dates,
                user_id,
            )
            flash("Delegates added successfully.", "success")
        except Exception as e:
            logging.error(f"Error adding delegates: {str(e)}")
            flash(f"Error adding delegates: {str(e)}", "danger")
        finally:
            if connection:
                connection.close()

        return redirect(url_for("add_delegate"))

    return render_template("add_delegate.html")


# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
