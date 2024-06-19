from flask import Flask, render_template
import credentials
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=credentials.host,
            user=credentials.user,
            password=credentials.password,
            database=credentials.database
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None


@app.route('/')
def per_meal_prep():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM well_done.v_per_meal_prep")
    results = cursor.fetchall()
    column_names = cursor.column_names
    cursor.close()
    conn.close()
    return render_template('index.html', data=results, columns=column_names)

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host=credentials.server_host, port=credentials.server_port)
