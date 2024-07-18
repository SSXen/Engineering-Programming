from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Store the latest LDR value
latest_ldr_value = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data', methods=['POST'])
def receive_data():
    global latest_ldr_value
    data = request.json
    latest_ldr_value = data.get['ldr_value']

    print(f"Received LDR value: {latest_ldr_value}")
    return jsonify({"status": "success", "ldr_value": latest_ldr_value}), 200

@app.route('/latest', methods=['GET'])
def latest():
    return jsonify({"ldr_value": latest_ldr_value}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)  # Specify your desired port here
