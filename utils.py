#!/usr/bin/env python3
import requests
import uuid
import sys
import re
import builtins
import os
import time

# Constantes de Cores
R = '\033[31m' # red
G = '\033[32m' # green
C = '\033[36m' # cyan
W = '\033[0m'  # white

def log_event(message, level="INFO"):
    """
    Função simples para escrever logs no console e em um arquivo de log específico.
    Isso é útil para rastrear o comportamento do script Python.
    """
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] [{level}] {message}"
    
    # Escreve no console (usando a função print corrigida)
    print(log_message)
    
    # Tenta escrever em um arquivo de log (no diretório raiz)
    try:
        with open("logs/python_events.log", "a") as f:
            f.write(log_message + "\n")
    except Exception as e:
        # Se falhar a escrita do log, apenas ignoramos para não travar o script principal
        pass

def downloadImageFromUrl(url, path):
    """
    Baixa uma imagem de uma URL com tratamento de erros de rede e timeout.
    Retorna o caminho completo do arquivo ou None em caso de falha.
    """
    if not url.startswith('http'):
        log_event(f"Tentativa de download com URL inválida: {url}", "WARN")
        return None
        
    try:
        # Timeout para evitar que o script trave em conexões lentas
        response = requests.get(url, timeout=15)
        response.raise_for_status() # Lança exceção para códigos de status HTTP 4xx/5xx
        
        # Gera nome único para evitar cache
        file_extension = ".jpg" # Assumimos JPG para simplificar
        fPath = os.path.join(path, str(uuid.uuid1()) + file_extension)
        
        with open(fPath, 'wb') as handler:
            handler.write(response.content)
            
        log_event(f"Download de imagem bem-sucedido: {url} -> {fPath}", "INFO")
        return fPath
        
    except requests.exceptions.Timeout:
        log_event(f"Timeout ao tentar baixar imagem de: {url}", "ERROR")
        return None
    except requests.exceptions.RequestException as e:
        log_event(f"Erro de requisição ao baixar {url}: {e}", "ERROR")
        return None
    except Exception as e:
        log_event(f"Erro desconhecido durante o download: {e}", "ERROR")
        return None


def print(ftext, **args):
    """
    Função print customizada que remove códigos de cor (ANSI escape codes)
    quando o script não está sendo executado em um terminal real (como acontece no PHP).
    Corrige o re.PatternError que ocorria anteriormente.
    """
    # Verifica se a saída padrão é um terminal interativo (tty)
    if os.isatty(sys.stdout.fileno()):
        builtins.print(ftext, flush=True, **args)
    else:
        # O código Octal \033 é o código de escape ANSI.
        # Substituímos a sequência de cores e a sequência de escape por um espaço ou nada.
        
        # 1. Substitui a sequência de escape Octal (\033) por um literal (\\33) para que o re.sub funcione corretamente
        ftext_escaped = ftext.replace('\033', '\\33')
        
        # 2. Usa regex para remover todas as sequências de cores (\33[XXXm)
        ftext_cleaned = re.sub(r'\\33\[\d+m', '', ftext_escaped)
        
        # 3. Imprime a versão limpa
        builtins.print(ftext_cleaned, flush=True, **args)

# Chamamos a função log_event no final para inicializar o arquivo de log se necessário
log_event("Módulo Utils carregado com sucesso.", "INFO")