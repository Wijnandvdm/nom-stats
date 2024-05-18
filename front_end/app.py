from flask import Flask, render_template
import mysql.connector
import credentials
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
def index():
    return "Welcome to the database view application!"

@app.route('/per_mealprep')
def per_mealprep():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM raw.v_per_ingredient")
    results = cursor.fetchall()
    column_names = cursor.column_names
    cursor.close()
    conn.close()
    return render_template('index.html', data=results, columns=column_names)


@app.route('/per_ingredient')
def per_ingredient():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM raw.v_per_ingredient")
    results = cursor.fetchall()
    column_names = cursor.column_names
    cursor.close()
    conn.close()
    return render_template('index.html', data=results, columns=column_names)

if __name__ == '__main__':
    app.run(debug=True)
