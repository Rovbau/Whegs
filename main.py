#! python
# -*- coding: utf-8 -*-
from Whegs import Whegs
from threading import Thread
from flask import Flask, request, redirect, render_template
import atexit
import logging

app = Flask(__name__)
whegs = Whegs()
logging.basicConfig(level=logging.ERROR, format='\n%(asctime)s %(message)s', filename='ExeptionLog.log')
logging.getLogger().addHandler(logging.StreamHandler())

@app.route('/')
def api_index():
    return render_template('index.html')

@app.route('/status')
def api_status():
    global whegs
    status_data = whegs.get_status_data()
    return render_template('status.html', status_data=status_data)

@app.route('/control', methods = ['GET'])
def api_control_get():
    return render_template('control.html')

@app.route('/control', methods = ['POST'])
def api_control():
    global whegs

    action = request.form['action']
    whegs.action(action)

    return redirect('/control')

def run_api_server():
    app.run()

def main():
    try:
        api_server_thread = Thread(target=run_api_server, daemon=True)
        api_server_thread.start()
        
        whegs.init()
        whegs.run()
    except Exception as e:
        logging.exception("Main-Loop Failed:")
    

if __name__ == '__main__':
    main()
