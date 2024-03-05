import sqlite3
from flask import Flask, render_template, request, jsonify, send_file
from contextlib import closing
import os

# Create Flask app
app = Flask(__name__)

# Function to initialize the SQLite database
def init_db():
    db_path = 'cad.db'
    if not os.path.exists(db_path):
        with closing(connect_db()) as db:
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()

# Function to connect to the SQLite database
def connect_db():
    return sqlite3.connect('cad.db')

# Route to render the index page
@app.route('/')
def index():
    return render_template('index.html')

# Route to serve the notification sound file
@app.route('/notification.mp3')
def notification_sound():
    return send_file('notification.mp3', as_attachment=False)

@app.route('/get_call/<int:call_id>', methods=['GET'])
def get_call(call_id):
    with closing(connect_db()) as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM calls WHERE id = ?", (call_id,))
        call = cursor.fetchone()

    if call:
        call_dict = {'id': call[0], 'address': call[1], 'name': call[2], 'description': call[3], 
                     'status': call[4], 'units': call[5], 'history': call[6]}
        return jsonify(call_dict)
    else:
        return jsonify({'error': 'Call not found'}), 404
    
# Route to handle deleting a call by ID
@app.route('/delete_call/<int:call_id>', methods=['DELETE'])
def delete_call(call_id):
    with closing(connect_db()) as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM calls WHERE id = ?", (call_id,))
        db.commit()
    
    return jsonify({'message': f'Call with ID {call_id} deleted successfully'})

# Route to handle adding a new call
@app.route('/add_call', methods=['POST'])
def add_call():
    data = request.get_json()
    address = data['address']
    name = data['name']
    description = data['description']
    status = data['status']
    units = data['units']
    history = "Created"
    
    # Convert units list to a string
    units_str = ', '.join(units)
    
    with closing(connect_db()) as db:
        cursor = db.cursor()
        cursor.execute("INSERT INTO calls (address, name, description, status, units, history) VALUES (?, ?, ?, ?, ?, ?)",
                       (address, name, description, status, units_str, history))
        db.commit()
    
    return jsonify({'message': 'Call added successfully'})

# Route to handle updating call status
@app.route('/update_call_status/<int:call_id>', methods=['POST'])
def update_call_status(call_id):
    data = request.get_json()
    new_status = data['status']
    
    with closing(connect_db()) as db:
        cursor = db.cursor()
        cursor.execute("UPDATE calls SET status = ? WHERE id = ?", (new_status, call_id))
        db.commit()
    
    return jsonify({'message': 'Call status updated successfully'})

# Route to handle attaching unit to call
@app.route('/attach_unit/<int:call_id>/<unit>', methods=['GET'])
def attach_unit(call_id, unit):
    with closing(connect_db()) as db:
        cursor = db.cursor()
        cursor.execute("SELECT units FROM calls WHERE id = ?", (call_id,))
        existing_units = cursor.fetchone()[0]
        
        if existing_units:
            units = existing_units + ', ' + unit
        else:
            units = unit
        
        cursor.execute("UPDATE calls SET units = ? WHERE id = ?", (units, call_id))
        db.commit()
    
    return jsonify({'message': 'Unit attached successfully'})

# Route to get all calls
@app.route('/get_calls', methods=['GET'])
def get_calls():
    with closing(connect_db()) as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM calls")
        calls = cursor.fetchall()
    
    calls_dict = [{'id': call[0], 'address': call[1], 'name': call[2], 'description': call[3], 
                   'status': call[4], 'units': call[5], 'history': call[6]} for call in calls]
    
    return jsonify(calls_dict)

# Run the Flask app
if __name__ == '__main__':
    init_db()  # Initialize database before running the app
    app.run(host="127.0.0.1", port="6042")
