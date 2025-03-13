from flask import Flask, render_template, jsonify
from bs4 import BeautifulSoup
import requests
from datetime import datetime

app = Flask(__name__)

# Configuration
URL = "https://cyberrange-sec.ciscoctf.io/%F0%9F%8F%86%E2%9A%A1%F0%9F%9A%A9/teams?e=7SL1EB"  # Replace with actual URL
REFRESH_INTERVAL = 60  # seconds


def fetch_and_parse_data():
  """Fetch and parse HTML data from the URL"""
  try:
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    missions = []
    for table_container in soup.select('div.table-responsive'):
      table = table_container.find('table')
      if table:
        for row in table.select('tbody tr'):
          cols = row.select('td')
          if len(cols) >= 3:
            mission = cols[1].text.strip()
            section = cols[2].text.strip()
            missions.append((mission, section))

    # Calculate frequency
    frequency = {}
    for mission, section in missions:
      key = (mission, section)
      frequency[key] = frequency.get(key, 0) + 1

    # Sort by frequency and mission name
    sorted_data = sorted(frequency.items(),key=lambda x: (-x[1], x[0][0]))

    return {
      "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "data": [{"count": c, "mission": m, "section": s}for (m, s), c in sorted_data]
    }

  except Exception as e:
    return {"error": str(e)}


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/api/leaderboard')
def leaderboard_api():
  return jsonify(fetch_and_parse_data())


if __name__ == '__main__':
  app.run()
