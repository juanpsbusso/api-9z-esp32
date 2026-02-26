from flask import Flask, jsonify
import requests
import re
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

@app.route('/')
def home():
    return "API 9z Operativa. Entra a /9z_data"

@app.route('/9z_data')
def get_9z_data():
    rival = "TBD"
    fecha = "Pronto"
    hora = "--:--"
    
    # Liquipedia exige un User-Agent para no bloquearnos
    headers = {
        'User-Agent': 'ESP32-9z-Monitor/1.0 (contacto@tuemail.com)'
    }
    
    try:
        # Descargamos el HTML directo de la página de 9z en Liquipedia
        r = requests.get('https://liquipedia.net/counterstrike/9z_Team', headers=headers, timeout=8)
        
        if r.status_code == 200:
            html = r.text
            
            # 1. Aislamos la cajita de "Upcoming Matches"
            match_block = re.search(r'infobox_matches_content(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
            
            if match_block:
                block = match_block.group(1)
                
                # 2. Extraemos los equipos (Liquipedia usa "data-highlightingclass" para los nombres)
                teams = re.findall(r'data-highlightingclass="([^"]+)"', block)
                if len(teams) >= 2:
                    t1, t2 = teams[0], teams[1]
                    # Identificamos cuál es el rival
                    if '9z' in t1.lower():
                        rival = t2
                    else:
                        rival = t1
                    
                    # Limpiamos palabras que ocupan lugar en la pantallita OLED
                    rival = rival.replace(" Esports", "").replace(" Team", "").replace(" Academy", " Ac")
                
                # 3. Extraemos el Timestamp exacto
                ts_match = re.search(r'data-timestamp="(\d+)"', block)
                if ts_match:
                    unix_time = int(ts_match.group(1))
                    
                    # Convertimos de UTC a Hora Argentina (-3)
                    dt_utc = datetime.fromtimestamp(unix_time, timezone.utc)
                    dt_arg = dt_utc - timedelta(hours=3)
                    
                    fecha = dt_arg.strftime("%d/%m")
                    hora = dt_arg.strftime("%H:%M")
                    
    except Exception as e:
        print("Error de Extracción:", e)
        rival = "API ERR"

    return jsonify({
        # Cortamos el nombre a 10 letras para que no desborde tu pantalla
        "rival": rival.upper()[:10], 
        "fecha": fecha,
        "hora": hora,
        "vrs": 1250 # Siguiente desafío: automatizar esto
    })

if __name__ == '__main__':
    app.run(debug=True)from flask import Flask, jsonify
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route('/9z_data')
def get_9z_data():
    rival = "TBD"
    fecha = "Pronto"
    hora = "--:--"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        url_rss = "https://www.hltv.org/rss/matches"
        
        r = requests.get(url_rss, headers=headers, timeout=8)
        
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            for item in root.findall('./channel/item'):
                title = item.find('title').text
                
                # Buscamos a 9z
                if '9z' in title.lower():
                    equipos = title.lower().replace(' vs ', '|').split('|')
                    if '9z' in equipos[0]:
                        rival = title.split(' vs ')[1][:10]
                    else:
                        rival = title.split(' vs ')[0][:10]
                    
                    pubDate = item.find('pubDate').text
                    partes = pubDate.split(' ')
                    fecha = f"{partes[1]} {partes[2]}"
                    
                    hora_gmt = int(partes[4].split(':')[0])
                    hora_arg = (hora_gmt - 3) % 24
                    minutos = partes[4].split(':')[1]
                    hora = f"{hora_arg:02d}:{minutos}"
                    break
    except Exception as e:
        print("Error:", e)
        rival = "API ERR"

    # Puntos VRS hardcodeados por ahora
    vrs_puntos = 1250 
    
    return jsonify({
        "rival": rival.upper(),
        "fecha": fecha,
        "hora": hora,
        "vrs": vrs_puntos
    })

# Formato requerido por Vercel
if __name__ == '__main__':
    app.run(debug=True)
