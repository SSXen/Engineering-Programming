from flask import Flask, redirect, render_template, url_for, request, jsonify, flash
import mysql.connector
from mysql.connector import Error
from typing import Optional, Dict, Any #mport  typing modules

app = Flask(__name__)
app.secret_key = 'ZenSign$'

# Database connection
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='ZenSign$',
        database='FloodlightDb'
    )
    return connection

@app.route('/')
def base_page():
    # Render the base page
    return render_template('base.html')

@app.route('/home')
def home_page():
    # Render the home page
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Handle login functionality
    if request.method == 'POST':
        # Get login details from the form
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Query to verify user credentials
        query = """
        SELECT * FROM users WHERE username=%s AND password=%s AND user_type=%s
        """
        cursor.execute(query, (username, password, user_type))
        user = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if user:
            # Redirect based on user type
            if user_type == 'admin':
                return redirect(url_for('admindash'))
            else:
                return redirect(url_for('userdash', username=username))
        else:
            flash('Invalid username, password, or user type')
            return redirect(url_for('login'))
    else:
        # Render the login page
        return render_template('login.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    # Handle registration functionality
    if request.method == 'POST':
        # Get registration details from the form
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Check if the username already exists
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            flash("Username already exists. Please choose a different one.")
            cursor.close()
            connection.close()
            return redirect(url_for("register"))
        
        # Insert new user into the database
        cursor.execute("""
        INSERT INTO users (username, password, user_type) VALUES (%s, %s, %s)
        """, (username, password, user_type))
        connection.commit()
        cursor.close()
        connection.close()

        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))
    else:
        # Render the registration page
        return render_template("register.html")

@app.route('/admindash')
def admindash():
    # Display the admin dashboard with sample items
    items = [
        {'id': 1, 'Student': 'Node1', 'StudentNum': '1234'},
        {'id': 2, 'Student': 'Node2', 'StudentNum': '1234'},
        {'id': 3, 'Student': 'Node2', 'StudentNum': '1234'},
        {'id': 4, 'Student': 'Node3', 'StudentNum': '1234'}
    ]
    return render_template('admindash.html', items=items)

@app.route('/userdash')
def userdash():
    # Display the user dashboard
    return render_template('userdash.html')

@app.route('/nodeview')
def nodeview():
    # Display the node view page
    return render_template('nodeview.html')

@app.route('/data', methods=['POST'])
def receive_data():
    # Handle incoming data from sensors
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"status": "error", "message": "Invalid JSON data"}), 400

        # Extract sensor data
        sensor_id = data.get('sensor_id', '221917845')
        light_intensity = data.get('ldr_value', 0)
        location = '192.168.0.124'  # Static location for all data points
        
        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert sensor data into the database
        query = """
        INSERT INTO sensorData (sensor_id, light_intensity, location) VALUES (%s, %s, %s)
        """
        cursor.execute(query, (sensor_id, light_intensity, location))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"status": "success", "ldr_value": light_intensity}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "An error occurred"}), 500

@app.route('/latest', methods=['GET'])
def latest():
    # Fetch the latest sensor data
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM sensorData ORDER BY timestamp DESC LIMIT 1")
    latest_data = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if latest_data and isinstance(latest_data, dict):
        # Return the latest sensor data as JSON
        return jsonify({
            "ldr_value": latest_data.get('light_intensity'),
            "sensor_id": latest_data.get('sensor_id'),
            "location": latest_data.get('location'),
            "timestamp": latest_data.get('timestamp')
        }), 200
    else:
        return jsonify({"ldr_value": None}), 200

@app.route('/all_data', methods=['GET'])
def all_data():
    # Fetch all sensor data
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM sensorData ORDER BY timestamp DESC")
    data = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    # Return all sensor data as JSON
    return jsonify(data), 200

if __name__ == '__main__':
    # Run the Flask application
    app.run(host='0.0.0.0', port=8080 )
