import os
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- IMPORT YOUR SCRAPERS ---
# Make sure scrape_airblue.py and scrape_flyjinnah.py are in the same folder
from scrape_airblue import get_airblue_flights
from scrape_flyjinnah import get_flyjinnah_prices

app = Flask(__name__)

# 1. Enable CORS 
# This allows your HTML website (hosted anywhere) to talk to this Python server
CORS(app)

# 2. Add Rate Limiting (Security)
# This prevents one person from crashing your server by spamming searches.
# We allow 10 requests per minute per IP address.
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute"],
    storage_uri="memory://"
)

# --- THREAD WRAPPERS ---
# These functions run the scrapers safely so one error doesn't crash the whole server

def run_airblue(origin, dest, date, results_list):
    """Runs Airblue scraper in a background thread"""
    try:
        data = get_airblue_flights(origin, dest, date)
        if data:
            results_list.extend(data)
    except Exception as e:
        print(f"❌ Airblue Thread Failed: {e}")

def run_flyjinnah(origin, dest, date, results_list):
    """Runs Fly Jinnah scraper in a background thread"""
    try:
        data = get_flyjinnah_prices(origin, dest, date)
        if data:
            results_list.extend(data)
    except Exception as e:
        print(f"❌ Fly Jinnah Thread Failed: {e}")

# --- API ROUTES ---

@app.route('/')
def home():
    return "Flight Scraper API is Running! Use the /search_flights endpoint."

@app.route('/search_flights', methods=['GET'])
@limiter.limit("5 per minute") # Strict limit for the heavy search task
def search_flights():
    # 1. Get Parameters from URL (sent by your HTML)
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    date = request.args.get('date') # Expected format: YYYY-MM-DD
    
    # Validation
    if not origin or not destination or not date:
        return jsonify({"error": "Missing parameters. Required: origin, destination, date"}), 400

    print(f"\n🚀 STARTING PARALLEL SEARCH: {origin} -> {destination} on {date}")
    
    # Shared list to store results from both threads
    all_results = []

    # 2. Create Threads
    # We pass the 'all_results' list to both threads so they can fill it up
    t1 = threading.Thread(target=run_airblue, args=(origin, destination, date, all_results))
    t2 = threading.Thread(target=run_flyjinnah, args=(origin, destination, date, all_results))

    # 3. Start Both Scrapers INSTANTLY
    t1.start()
    t2.start()

    # 4. Wait for both to finish (The total wait time is only as long as the slowest one)
    t1.join()
    t2.join()

    print(f"✅ FINISHED. Sending {len(all_results)} flights.")
    return jsonify(all_results)

if __name__ == '__main__':
    # PORT CONFIGURATION FOR CLOUD HOSTING
    # Render/Heroku will set the PORT environment variable. 
    # If running locally, it defaults to 5000.
    port = int(os.environ.get('PORT', 5000))
    
    # threaded=True allows multiple users to search at the same time
    app.run(host='0.0.0.0', port=port, threaded=True)