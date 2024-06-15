import psycopg2
import os
from flask import flash
import logging


def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )


def execute_query(connection, query, params=None):
    cursor = connection.cursor()
    cursor.execute(query, params)
    cursor.close()


def create_table(connection, table_name, columns):
    columns_def = ", ".join(f"{col} {datatype}" for col, datatype in columns.items())
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def});"
    execute_query(connection, create_table_query)


def insert_record(connection, table_name, record, conflict_columns=None):
    columns = ", ".join(record.keys())
    placeholders = ", ".join(["%s"] * len(record))
    conflict_clause = ""
    if conflict_columns:
        conflict_clause = f"ON CONFLICT ({', '.join(conflict_columns)}) DO NOTHING"

    insert_query = f"""
        INSERT INTO {table_name} ({columns})
        VALUES ({placeholders})
        {conflict_clause};
    """
    execute_query(connection, insert_query, list(record.values()))


def load_table_data(connection, table_name, df, upload_timestamp, upload_user):
    for index, row in df.iterrows():
        record = row.to_dict()
        record.update(
            {"upload_timestamp": upload_timestamp, "upload_user": upload_user}
        )
        insert_record(
            connection,
            table_name,
            record,
            conflict_columns=["engagement_id", "creation_date"],
        )


def create_engagement_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS engagement (
        engagement_id TEXT,
        creation_date TIMESTAMP,
        release_date TIMESTAMP,
        last_time_charged_date TIMESTAMP,
        last_expenses_charged_date TIMESTAMP,
        last_active_etcp_date TIMESTAMP,
        engagement TEXT,
        client TEXT,
        engagement_partner TEXT,
        engagement_partner_gui TEXT,
        engagement_manager TEXT,
        engagement_manager_gui TEXT,
        engagement_partner_service_line TEXT,
        engagement_status TEXT,
        last_etc_date TIMESTAMP,
        report_date TIMESTAMP,
        etc_age INTEGER,
        upload_timestamp TIMESTAMP,
        upload_user TEXT,
        UNIQUE (engagement_id, creation_date)
    );
    """
    execute_query(connection, create_table_query)


def create_delegates_table(connection):
    columns = {
        "id": "SERIAL PRIMARY KEY",
        "engagement_id": "INTEGER NOT NULL",
        "delegate_number": "TEXT NOT NULL",
        "delegate_name": "TEXT NOT NULL",
        "delegate_gui": "TEXT NOT NULL",
        "delegate_email": "TEXT NOT NULL",
        "end_date": "TIMESTAMP",
        "added_by": "TEXT NOT NULL",
        "added_timestamp": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    }
    create_table(connection, "delegates", columns)


def load_engagement_data(df, upload_timestamp, upload_user):
    try:
        connection = get_db_connection()
        create_engagement_table(connection)
        load_table_data(connection, "engagement", df, upload_timestamp, upload_user)
        connection.close()
        flash("Data loaded into the database successfully!", "success")
    except Exception as e:
        flash(f"Error loading data into database: {str(e)}", "danger")
        logging.error(f"Error loading data into database: {str(e)}")


def load_delegate_data(delegates):
    try:
        connection = get_db_connection()
        create_delegates_table(connection)
        for delegate in delegates:
            record = {
                "engagement_id": delegate[0],
                "delegate_number": delegate[1],
                "delegate_name": delegate[2],
                "delegate_gui": delegate[3],
                "delegate_email": delegate[4],
                "end_date": delegate[5],
                "added_by": delegate[6],
            }
            insert_record(connection, "delegates", record)
        connection.close()
        flash("Delegates added successfully.", "success")
    except Exception as e:
        flash(f"Error adding delegates to database: {str(e)}", "danger")
        logging.error(f"Error adding delegates to database: {str(e)}")
