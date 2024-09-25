import mysql.connector
from mysql.connector import Error
import pandas as pd  # To export data to Excel
import os
from datetime import datetime
from sqlalchemy import create_engine
from mysql.connector import Error, errorcode



# Database configuration
db_config = {
    'user': 'admin',
    'password': 'Francisc0-1981',
    'host': '10.2.120.59',
    'database': 'fulfillment',
    'port': 3306
}


def insert_activation_error(ticket_id, serial_number, sim_number, error_message):
    try:
        connection = mysql.connector.connect(
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            database=db_config['database'],
            port=db_config['port']
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            # Check if ticket_id already exists in the table
            check_query = "SELECT COUNT(*) FROM act_errors WHERE ticket_id = %s"
            cursor.execute(check_query, (ticket_id,))
            count = cursor.fetchone()[0]

            if count > 0:
                print(f"Ticket ID {ticket_id} already exists. Skipping insertion.")
                return

            # Prepare the insert statement with the date
            sql_insert_query = """INSERT INTO act_errors (ticket_id, IMEI, sim, error, date) 
                                  VALUES (%s, %s, %s, %s, %s)"""
            current_date = datetime.now()
            record_tuple = (ticket_id, serial_number, sim_number, error_message, current_date)

            print(f"Inserting into database: {record_tuple}")
            cursor.execute(sql_insert_query, record_tuple)
            connection.commit()
            print("Error information inserted successfully.")
    
    except mysql.connector.Error as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            print(f"Duplicate entry for ticket_id: {ticket_id}. Error: {e}")
        else:
            print(f"Error while connecting to MySQL: {e}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def fetch_activation_errors(start_date, end_date):
    try:
        connection = mysql.connector.connect(
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            database=db_config['database'],
            port=db_config['port']
        )
        if connection.is_connected():
            cursor = connection.cursor()
            
            # SQL query to fetch filtered data based on start_date and end_date
            sql_query = """
            SELECT * FROM act_errors
            WHERE DATE(date) BETWEEN %s AND %s
            ORDER BY date ASC
            """
            
            cursor.execute(sql_query, (start_date, end_date))
            result = cursor.fetchall()
            
            # Fetch column names
            columns = [desc[0] for desc in cursor.description]
            
            # Convert the result to a DataFrame
            df = pd.DataFrame(result, columns=columns)
            return df
    except Error as e:
        print(f"Error fetching activation errors: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()



def export_to_excel(df, file_path):
    try:
        df.to_excel(file_path, index=False)
        print(f"Data exported to {file_path}")
    except Exception as e:
        print(f"Error exporting to Excel: {e}")


def open_directory(file_path):
    directory = os.path.dirname(file_path)
    os.startfile(directory)  # Opens the file explorer in the directory
    
    
    
    
def fetch_available_dates():
    try:
        connection = mysql.connector.connect(
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            database=db_config['database'],
            port=db_config['port']
        )
        if connection.is_connected():
            cursor = connection.cursor()
            # Fetch distinct dates (without time)
            sql_query = "SELECT DISTINCT DATE(date) FROM act_errors ORDER BY DATE(date) ASC;"
            cursor.execute(sql_query)
            dates = cursor.fetchall()

            # Debugging: Check the fetched dates
            print("Fetched Dates:", dates)

            # Extract only the dates
            return [date[0].strftime('%Y-%m-%d') for date in dates if date[0] is not None]
    except Error as e:
        print(f"Error fetching available dates: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
            
            
            
def fetch_activation_error_by_ticket_id_and_sim(ticket_id, sim_number):
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            sql_query = "SELECT * FROM act_errors WHERE ticket_id = %s AND sim = %s"
            cursor.execute(sql_query, (ticket_id, sim_number))
            result = cursor.fetchone()
            return result  # Return the entry if found, None otherwise
    except Error as e:
        print(f"Error fetching activation error: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def delete_activation_error(ticket_id):
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            sql_query = "DELETE FROM act_errors WHERE ticket_id = %s"
            cursor.execute(sql_query, (ticket_id,))
            connection.commit()
            print(f"Deleted Ticket ID {ticket_id} from the database.")
    except Error as e:
        print(f"Error deleting activation error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
