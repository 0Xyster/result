
import requests
from bs4 import BeautifulSoup
import time
import json
from flask import Flask
from threading import Thread
import os

# 🔐 Replace this after generating your own Pushbullet token
API_KEY = "o.ceJB2iCtz4jgKZ54pkwVBvVnkPkKHbQD"
URL = "https://results.digilocker.gov.in/"

app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!"

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

def get_structure_snapshot(html):
    soup = BeautifulSoup(html, 'html.parser')
    return {
        "div": len(soup.find_all('div')),
        "img": len(soup.find_all('img')),
        "button": len(soup.find_all('button')),
        "input": len(soup.find_all('input')),
        "select": len(soup.find_all('select')),
    }

def significant_change(before, after):
    for tag in before:
        if abs(before[tag] - after.get(tag, 0)) >= 2:
            return True
    return False

def send_notification(title, body):
    data = {"type": "note", "title": title, "body": body}
    headers = {'Access-Token': API_KEY, 'Content-Type': 'application/json'}
    requests.post('https://api.pushbullet.com/v2/pushes',
                  data=json.dumps(data),
                  headers=headers)

def monitor_site():
    print("🔍 Taking first snapshot...")
    prev_snapshot = get_structure_snapshot(requests.get(URL).text)
    
    while True:
        time.sleep(90)  # check every 1.5 mins
        print("🔄 Checking for changes...")
        html = requests.get(URL).text
        new_snapshot = get_structure_snapshot(html)

        if significant_change(prev_snapshot, new_snapshot):
            print("🚨 CHANGE DETECTED!")
            send_notification("🚨 Layout Changed",
                            "DigiLocker Results page changed!")
            break
        else:
            print("✅ No change.")

if __name__ == '__main__':
    flask_thread = Thread(target=run_flask)
    monitor_thread = Thread(target=monitor_site)
    
    flask_thread.start()
    monitor_thread.start()
