from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime
import threading
from app import start_bot, stop_bot

app = Flask(__name__)

# Global state
bot_status = {
    "running": False,
    "start_time": None,
    "instances": 0,
    "success": False,
    "last_update": None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify(bot_status)

@app.route('/api/start', methods=['POST'])
def start():
    if not bot_status["running"]:
        data = request.json
        # Update config with new settings
        config = {
            'General': {
                'sale_time': data['sale_time'],
                'url': data['url'],
                'browser_instances': str(data['instances']),
                'retry_count': str(data['retry_count']),
                'retry_delay': str(data['retry_delay'])
            },
            'Tickets': {
                'categories': ','.join(data['categories']),
                'quantity': str(data['quantity'])
            }
        }
        
        with open('config.ini', 'w') as f:
            config.write(f)
        
        # Start bot in background thread
        thread = threading.Thread(target=start_bot, args=(bot_status,))
        thread.start()
        
        return jsonify({"status": "started"})
    return jsonify({"status": "already running"})

@app.route('/api/stop', methods=['POST'])
def stop():
    if bot_status["running"]:
        stop_bot()
        return jsonify({"status": "stopped"})
    return jsonify({"status": "not running"})

if __name__ == '__main__':
    app.run(debug=True, port=5000) 