import psycopg2
from flask import flash
import logging
import os


def create_table_if_not_exists(connection, table_name):
    cursor = connection.cursor()
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
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
        upload_user TEXT
    );
    """
    cursor.execute(create_table_query)
    cursor.close()


# TODO: #10 Reorder the columns into a more logical order
# e.g. primary key first, then foreign keys, then key meta data, date columns and then calc cols


def insert_data(connection, df, table_name, upload_timestamp, upload_user):
    cursor = connection.cursor()
    for index, row in df.iterrows():
        insert_query = f"""
        INSERT INTO {table_name} (
            engagement_id, creation_date, release_date, 
            last_time_charged_date, last_expenses_charged_date, 
            last_active_etcp_date, engagement, client, 
            engagement_partner, engagement_partner_gui, 
            engagement_manager, engagement_manager_gui, 
            engagement_partner_service_line, engagement_status, 
            last_etc_date, report_date, etc_age,
            upload_timestamp, upload_user
        ) SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM {table_name} 
            WHERE engagement_id = %s AND creation_date = %s
        );
        """
        cursor.execute(
            insert_query,
            tuple(row)
            + (
                upload_timestamp,
                upload_user,
                row["engagement_id"],
                row["creation_date"],
            ),
        )
    connection.commit()
    cursor.close()


def load_data_to_db(df, table_name, upload_timestamp, upload_user):
    try:
        connection = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        create_table_if_not_exists(connection, table_name)
        insert_data(connection, df, table_name, upload_timestamp, upload_user)
        connection.close()
        flash("Data loaded into the database successfully.", "success")
    except Exception as e:
        flash(f"Error loading data into database: {str(e)}", "danger")
        logging.error(f"Error loading data into database: {str(e)}")
