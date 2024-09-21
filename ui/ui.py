import matplotlib
import requests
from flask import Flask, render_template, jsonify, request
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64
import json

# Declare global variables
last_temp_read_x = 0
last_temp_read_y = 0
last_moisture_read_x = 0
last_moisture_read_y = 0

matplotlib.use('Agg')

# Instantiate flask app
app = Flask(__name__)

def generate_temp_graph(x, y):
    """Generates temperature graph"""
    plt.figure()
    plt.plot(x, y)
    plt.xlabel('Time (Seconds)')
    plt.ylabel('Degrees (°C)')
    plt.title('Temperature')

    # Save the plot to a bytes object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the bytes object to base64
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    return image_base64

def generate_moisture_graph(x, y):
    """Generates moisture graph"""
    plt.figure()
    plt.plot(x, y)
    plt.xlabel('Time (Seconds)')
    plt.ylabel('Moisture Level (%)')
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
    """Endpoint function that returns render template built from index.html"""

    graph_data_temp = generate_temp_graph(last_temp_read_x, last_temp_read_y)
    graph_data_moisture = generate_moisture_graph(last_moisture_read_x, last_moisture_read_y)

    # Render HTML template with graph data
    return render_template('index.html', graph_data_temp=graph_data_temp, graph_data_moisture=graph_data_moisture)


@app.route('/refresh', methods=['GET'])
def refresh():
    """Endpoint that generate new graphs and returns the graphs, settings
        and the light/pump states"""
    
    response = json.loads(requests.get("http://localhost:8000/get_readings").text)
    response2 = json.loads(requests.get("http://localhost:8000/get_settings").text)
    
    times = []
    temps = []
    moistures = []

    # Add data from sensor readings to appropriate arrays
    for field in response:
        time = field['time']
        times.append(time)
        
        temps.append(field['temp'])
        moistures.append(field['moisture'])

    # Convert the epoch times to time elapsed since the first reading
    min_time = min(times) if times else 0
    elapsed_times = []
    for time in times:
        elapsed_times.append(time - min_time)

    # Get assign settinfs to variables
    temp_setting = response2['temp_setting']
    moisture_setting = response2['moisture_setting']
    operating_mode = response2['operating_mode']

    # Get light and pump state
    response3 = json.loads(requests.get("http://localhost:8000/get_state").text)
    light = int(response3['light'])
    pump = int(response3['pump'])
    
    light = 'On' if light == 1 else 'Off'
    pump = 'On' if pump == 1 else 'Off'

    last_temp_read_x = elapsed_times
    last_temp_read_y = temps
    last_moisture_read_x = elapsed_times
    last_moisture_read_y = moistures

    # Generate the graph data
    graph_data_temp = generate_temp_graph(last_temp_read_x, last_temp_read_y)
    graph_data_moisture = generate_moisture_graph(last_moisture_read_x, last_moisture_read_y)

    # Return the new graph data as JSON
    return jsonify({
        'graph_data_temp': graph_data_temp,
        'graph_data_moisture': graph_data_moisture,
        'temp_setting': temp_setting,
        'moisture_setting': moisture_setting,
        'operating_mode': operating_mode,
        'light': light,
        'pump': pump
    })


@app.route('/clear_readings', methods=['GET'])
def clear_readings():
    """Endpoint function that will send an api request to clear the db"""

    requests.get("http://localhost:8000/clear_readings")
    return jsonify({'message': 'clear request received'})

@app.route('/change_settings', methods=['POST'])
def change_settings():
    """End point function that will send an api request to change settings
        in the db"""
    
    data = request.json
    requests.post("http://localhost:8000/change_settings/",json=data)
    return jsonify({'message': 'Settings received successfully'})

@app.route('/change_state', methods=['POST'])
def change_state():
    """Endpoint function that will send an api request to change light and
        pump state in the db"""
    
    data = request.json
    requests.post("http://localhost:8000/change_state/",json=data)
    return jsonify({'message': 'State received successfully'})


if __name__ == '__main__':
    app.run(debug=True)
