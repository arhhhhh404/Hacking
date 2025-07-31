from flask import Flask, request
from datetime import datetime
import requests

app = Flask(__name__)

def log_connection():
    with open("connections.log", "a") as log:
        log.write(f"[{datetime.now()}] IP: {request.remote_addr}, Agent: {request.headers.get('User-Agent')}\n")

def geolocaliser_ip(ip):
    url = f"http://ip-api.com/json/{ip}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            return {
                "IP" : data['query'],
                "Pays" : data['country'],
                "Région" : data['regionName'],
                "Ville" : data['city'],
                "Fournisseur" : data['isp'],
                "Latitude" : data['lat'],
                "Longitude" : data['lon'],
                "Fuseau horaire" : data['timezone'],
                }
    return {"Erreur": ""}

@app.route("/")
def index():
    ip = request.remote_addr
    info = geolocaliser_ip(ip)
    log_connection()

    # Générer le bloc HTML d'infos
    info_html = ""
    for key, value in info.items():
        info_html += f"<tr><td>{key}</td><td>{value}</td></tr>"

    return f'''
    <html>
        <head>
            <title>Web Control Panel</title>
            <style>
                body {{
                    background-color: #000;
                    color: #0f0;
                    font-family: monospace;
                    padding: 20px;
                }}
                h1 {{
                    color: red;
                    font-size: 3em;
                }}
                table {{
                    margin-top: 20px;
                    border-collapse: collapse;
                    width: 50%;
                }}
                td {{
                    border: 1px solid #0f0;
                    padding: 8px;
                }}
            </style>
        </head>
        <body>
            <h1>DUMBASS</h1>
            <p><strong>We see you.</strong> Here’s what we know:</p>
            <table>
                {info_html}
            </table>
        </body>
    </html>
    '''

@app.after_request
def modify_headers(response):
    response.headers['Server'] = 'Apache/2.4.7 (Debian)'
    response.headers['X-Powered-By'] = 'PHP/5.3.29'
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)