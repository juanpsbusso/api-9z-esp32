from flask import Flask, jsonify
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
