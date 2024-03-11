import matplotlib
import requests
matplotlib.use('Agg')  # Use the 'Agg' backend which does not require a display

from flask import Flask, render_template, jsonify, request
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64

last_temp_read_x = 0
last_temp_read_y = 0
last_moisture_read_x = 0
last_moisture_read_y = 0

app = Flask(__name__)

def generate_temp_graph(x, y):
    # Create a plot
    plt.figure()
    plt.plot(x, y)
    plt.xlabel('Time')
    plt.ylabel('Degrees (C)')
    plt.title('Temperature')

    # Save the plot to a bytes object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the bytes object to base64
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    return image_base64

def generate_moisture_graph(x, y):
     # Create a plot
    plt.figure()
    plt.plot(x, y)
    plt.xlabel('Time')
    plt.ylabel('Moisture Level')
    plt.title('Soil Moisture')

    # Save the plot to a bytes object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the bytes object to base64
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    return image_base64

@app.route('/')
def index():
    # Generate graph
    graph_data_temp = generate_temp_graph(last_temp_read_x, last_temp_read_y)
    graph_data_moisture = generate_moisture_graph(last_moisture_read_x, last_moisture_read_y)

    # Render HTML template with graph data
    return render_template('index.html', graph_data_temp=graph_data_temp, graph_data_moisture=graph_data_moisture)

@app.route('/refresh', methods=['GET'])
def refresh():
    # Generate new graph data
    response = requests.get("http://localhost:8000/get_readings")
    response2 = requests.get("http://localhost:8000/get_settings")
    response_body = response.text
    times = []
    temps = []
    moistures = []
    response_body = response_body[1:-1]

    fields = response_body.split(",")

    for field in fields:
        if 'time' in field:
            times.append(int(field[8:]))
        if 'temp' in field:
            temps.append(float(field[8:]))
        if 'moisture' in field:
            moistures.append(float(field[12:-1]))

    response_body2 = response2.text
    response_body2 = response_body2[1:-1]
    fields = response_body2.split(",")
    for field in fields:
        if 'temp_setting' in field:
            temp_setting = field[34:-1]
        if 'moisture_setting' in field:
            moisture_setting = field[41:-1]
        if 'operating_mode' in field:
            operating_mode = field[39:-4]

    response3 = requests.get("http://localhost:8000/get_state")
    response_body3 = response3.text
    response_body3 = response_body3[1:-1]
    fields = response_body3.split(",")
    light = 0
    pump = 0
    for field in fields:
        if 'light' in field:
            light = field[9:]
            if light == '0':
                light = 'Off'
            else:
                light = 'On'
        if 'pump' in field:
            pump = field[7:-1]
            if pump == '0':
                pump = 'Off'
            else:
                pump = 'On'

    last_temp_read_x = times
    last_temp_read_y = temps
    last_moisture_read_x = times
    last_moisture_read_y = moistures

    graph_data_temp = generate_temp_graph(last_temp_read_x, last_temp_read_y)
    graph_data_moisture = generate_moisture_graph(last_moisture_read_x, last_moisture_read_y)

    # Return the new graph data as JSON
    return jsonify({'graph_data_temp': graph_data_temp, 'graph_data_moisture': graph_data_moisture, 'temp_setting': temp_setting, 'moisture_setting': moisture_setting, 'operating_mode': operating_mode, 'light': light, 'pump': pump})

@app.route('/receive_input', methods=['GET'])
def receive_input():
    requests.get("http://localhost:8000/receive_input")
    return jsonify({'message': 'Read request received'})

@app.route('/get_state', methods=['GET'])
def get_state():
    response = requests.get("http://localhost:8000/get_state")
    response_body = response.text
    response_body = response_body[1:-1]
    fields = response_body.split(",")
    light = 0
    pump = 0
    for field in fields:
        if 'light' in field:
            light = field
        if 'pump' in field:
            pump = field
    return jsonify({'light': light, 'pump': pump})

@app.route('/clear_readings', methods=['GET'])
def clear_readings():
    requests.get("http://localhost:8000/clear_readings")
    return jsonify({'message': 'clear request received'})

@app.route('/change_settings', methods=['POST'])
def change_settings():
    data = request.json
    requests.post("http://localhost:8000/change_settings/",json=data)
    return jsonify({'message': 'Settings received successfully'})

@app.route('/change_state', methods=['POST'])
def change_state():
    data = request.json
    requests.post("http://localhost:8000/change_state/",json=data)
    return jsonify({'message': 'State received successfully'})

if __name__ == '__main__':
    app.run(debug=True)
