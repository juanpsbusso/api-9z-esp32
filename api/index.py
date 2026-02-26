from flask import Flask, jsonify
import requests
import re
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

@app.route('/')
def home():
    return "API 9z Operativa. Entra a /9z_data"

@app.route('/9z_data')
def get_9z_data():
    rival = "SIN PARTIDO"
    fecha = "--/--"
    hora = "--:--"
    debug_status = "ok"

    try:
        # TRUCO DE INGENIERÍA: Usamos AllOrigins para enmascarar la IP de Vercel
        proxy_url = "https://api.allorigins.win/raw?url=https://liquipedia.net/counterstrike/9z_Team"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        # Le damos un poco más de tiempo por el salto extra del proxy
        r = requests.get(proxy_url, headers=headers, timeout=12)
        
        if r.status_code == 200:
            html = r.text
            
            # 1. Aislar la tabla de próximos partidos
            match_block = re.search(r'infobox_matches_content(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
            
            if match_block:
                block = match_block.group(1)
                
                # 2. Extraer equipos
                teams = re.findall(r'data-highlightingclass="([^"]+)"', block)
                if len(teams) >= 2:
                    t1, t2 = teams[0], teams[1]
                    rival_full = t2 if '9z' in t1.lower() else t1
                    
                    # Limpiamos palabras largas para la OLED
                    rival = rival_full.replace(" Esports", "").replace(" Team", "").replace(" Academy", " Ac")
                    rival = rival[:10].upper()
                
                # 3. Extraer hora exacta (Timestamp Unix)
                ts_match = re.search(r'data-timestamp="(\d+)"', block)
                if ts_match:
                    unix_time = int(ts_match.group(1))
                    
                    # Convertir a Hora Argentina (UTC-3)
                    dt_utc = datetime.fromtimestamp(unix_time, timezone.utc)
                    dt_arg = dt_utc - timedelta(hours=3)
                    
                    fecha = dt_arg.strftime("%d/%m")
                    hora = dt_arg.strftime("%H:%M")
            else:
                debug_status = "HTML sin tabla (Cambio de estructura)"
        else:
            debug_status = f"HTTP {r.status_code} desde proxy"
            
    except Exception as e:
        debug_status = str(e)[:25]

    return jsonify({
        "rival": rival,
        "fecha": fecha,
        "hora": hora,
        "vrs": 1250,
        "debug": debug_status # Si algo falla, esto nos dirá qué fue
    })

if __name__ == '__main__':
    app.run(debug=True)
