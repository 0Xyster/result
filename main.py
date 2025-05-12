from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from playsound import playsound
import time
import threading
import requests
from flask import Flask

# === Setup Flask ===
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ I'm alive!"

# === Start Flask Web Server in a Thread ===
def run_flask():
    app.run(host="0.0.0.0", port=8080)

flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# === Self-ping Every 4 Minutes to Stay Awake ===
def self_ping():
    while True:
        try:
            requests.get("https://result-kjrc.onrender.com")
            print("🔁 Self-pinged to stay awake")
        except Exception as e:
            print(f"⚠️ Self-ping failed: {e}")
        time.sleep(240)  # every 4 minutes

ping_thread = threading.Thread(target=self_ping)
ping_thread.daemon = True
ping_thread.start()

# === Selenium Setup ===
service = Service("chromedriver.exe")
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=service, options=chrome_options)

url = "https://results.digilocker.gov.in/"
driver.get(url)

def get_structure_snapshot():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    structure = {
        "div": len(soup.find_all('div')),
        "img": len(soup.find_all('img')),
        "button": len(soup.find_all('button')),
        "input": len(soup.find_all('input')),
        "select": len(soup.find_all('select')),
    }
    return structure

def significant_change(before, after):
    for tag in before:
        if abs(before[tag] - after.get(tag, 0)) >= 2:
            return True
    return False

# Initial snapshot
prev_snapshot = get_structure_snapshot()

while True:
    time.sleep(90)
    driver.refresh()
    print("🔄 Refreshed... checking for major changes.")
    time.sleep(5)

    new_snapshot = get_structure_snapshot()
    
    if significant_change(prev_snapshot, new_snapshot):
        print("🚨 Significant change detected in layout!")
        playsound("alert.mp3")
        break
    else:
        print("✅ No major layout change detected.")
