# login_system.py - VERSÃO COM ANIMAÇÃO VISUAL E CORREÇÃO DE URL

import os
import time
import subprocess
import hashlib
import sys
import requests
from colorama import init, Fore, Style

# Inicializa o Colorama
init(autoreset=True)

# --- CONFIGURAÇÕES DE VELOCIDADE DA ANIMAÇÃO ---
VELOCIDADE_LINHA = 0.05  # Atraso entre cada linha impressa
VELOCIDADE_MSG = 0.025
# -------------------------------------------------

# --- CLASSE DE CORES ---
class Cores:
    BRIGHT, RESET = Style.BRIGHT, Style.RESET_ALL
    AZUL, AMARELO, VERDE, VERMELHO, BRANCO, MAGENTA = Fore.CYAN + BRIGHT, Fore.YELLOW + BRIGHT, Fore.GREEN + BRIGHT, Fore.RED + BRIGHT, Fore.WHITE + BRIGHT, Fore.MAGENTA + BRIGHT
    BANNER, TITULO, BORDA, TEXTO, DESTAQUE = AZUL, AMARELO, BRANCO, Fore.LIGHTWHITE_EX, MAGENTA
    SUCESSO, ERRO, AVISO, INFO, STATUS = VERDE, VERMELHO, AMARELO, AZUL, BRANCO
    PROMPT, INPUT, HWID = BRANCO, Fore.LIGHTCYAN_EX, AZUL

# --- NOVA FUNÇÃO DE ANIMAÇÃO ---
def exibir_animado(texto_multilinha, velocidade=VELOCIDADE_LINHA):
    """Exibe um bloco de texto com várias linhas, uma por vez, para um efeito de animação."""
    for linha in texto_multilinha.strip().split('\n'):
        print(linha)
        time.sleep(velocidade)

def get_hwid():
    """Obtém o número de série do primeiro disco físico (HD/SSD) e o usa como HWID."""
    try:
        comando = 'wmic diskdrive get serialnumber'
        resultado = subprocess.check_output(comando, shell=True, text=True, stderr=subprocess.DEVNULL)
        linhas = resultado.strip().split('\n')
        hwid_bruto = linhas[1].strip() if len(linhas) > 1 else "DefaultHWID"
        return hashlib.sha256(hwid_bruto.encode()).hexdigest()
    except Exception:
        return "ERRO_AO_OBTER_HWID_DISCO"

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def exibir_banner_principal():
    """Exibe o banner e as informações principais de forma animada."""
    banner_arte = r"""
██╗  ██╗███╗   ██╗████████╗███████╗
██║ ██╔╝████╗  ██║╚══██╔══╝╚══███╔╝
█████╔╝ ██╔██╗ ██║   ██║     ███╔╝ 
██╔═██╗ ██║╚██╗██║   ██║    ███╔╝  
██║  ██╗██║ ╚████║   ██║   ███████╗
╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝
    """
    info = f"""
{Cores.BORDA}======================================================
{Cores.STATUS}[i] Auth System        : {Cores.SUCESSO}Online Server
{Cores.STATUS}[i] Security Source    : {Cores.SUCESSO}HWID
{Cores.BORDA}======================================================
"""
    print(Cores.BANNER + banner_arte)
    exibir_animado(info, 0.1)

def menu_principal():
    """Exibe o menu principal de forma animada."""
    menu_texto = f"""
{Cores.PROMPT}[1] Login
{Cores.PROMPT}[3] {Cores.AVISO}Mostrar meu HWID
{Cores.PROMPT}[0] Exit
    """
    exibir_animado(menu_texto)

def tela_de_login_servidor():
    """Função de login corrigida e com animação."""
    URL_BASE = "https://marin-login-api.onrender.com"
    URL_LOGIN = f"{URL_BASE}/api/login" # URL correta para o POST

    limpar_tela()
    exibir_banner_principal()
    print(Cores.TITULO + "--- TELA DE LOGIN (AUTENTICAÇÃO ONLINE) ---\n")

    try:
        print(f"{Cores.INFO}[*] Verificando o status do servidor...", end="", flush=True)
        requests.get(URL_BASE, timeout=60)
        print(f" {Cores.SUCESSO}Online!")
        time.sleep(1)
    except requests.exceptions.RequestException:
        print(f" {Cores.ERRO}Offline.")
        print(Cores.ERRO + "\n[ERROR] Não foi possível conectar ao servidor de autenticação.")
        time.sleep(3)
        return

    try:
        usuario_input = input(f"{Cores.PROMPT}[?] Digite seu usuário: {Cores.INPUT}")
        key_input = input(f"{Cores.PROMPT}[?] Digite sua key: {Cores.INPUT}")
        hwid_atual = get_hwid()

        if "ERRO" in hwid_atual:
            print(Cores.ERRO + "\n[FATAL] Não foi possível obter um ID de hardware válido.")
            time.sleep(3)
            return

        print(Cores.INFO + "\n[*] Autenticando credenciais...")
        print(Cores.AVISO + "(Isso pode levar até um minuto na primeira tentativa do dia)")

        dados_de_login = {"usuario": usuario_input, "key": key_input, "hwid": hwid_atual}
        
        response = requests.post(URL_LOGIN, json=dados_de_login, timeout=60) # Usando a URL correta

        if response.status_code == 200:
            resposta_json = response.json()
            if resposta_json.get("status") == "sucesso":
                print(f"\n{Cores.SUCESSO}[SUCCESS] {resposta_json.get('mensagem')}")
                time.sleep(2)
                tela_logado(usuario_input)
            else:
                print(f"\n{Cores.ERRO}[ERROR] {resposta_json.get('mensagem')}")
                time.sleep(3)
        else:
             mensagem_erro = response.json().get("mensagem", "Erro desconhecido.")
             print(f"\n{Cores.ERRO}[ERROR] {mensagem_erro} (Código: {response.status_code})")
             time.sleep(3)

    except requests.exceptions.RequestException:
        print(Cores.ERRO + "\n[ERROR] A conexão falhou ou o tempo de espera foi excedido.")
        time.sleep(3)
    except KeyboardInterrupt:
        print(Cores.ERRO + "\n\n[!] Operação cancelada. Saindo...")
        exit()

def tela_logado(nome_usuario):
    """Tela animada após o login bem-sucedido."""
    while True:
        limpar_tela()
        hwid_curto = get_hwid()[:10]
        
        tela_logado_texto = f"""
{Cores.SUCESSO}ACESSO AUTORIZADO
{Cores.BORDA}======================================================
{Cores.PROMPT}Bem-vindo, {Cores.INFO}{nome_usuario}{Cores.PROMPT}!
{Cores.TEXTO}Licença vinculada ao HWID: {Cores.SUCESSO}{hwid_curto}...
{Cores.BORDA}======================================================

{Cores.PROMPT}[1] Ativar Função A
{Cores.PROMPT}[2] Executar Ferramenta B
{Cores.PROMPT}[3] Logout
        """
        exibir_animado(tela_logado_texto)

        try:
            escolha = input(f"{Cores.PROMPT}[+] Escolha uma opção: {Cores.INPUT}")
            if escolha == '1':
                print(Cores.SUCESSO + "\n[+] Função A ativada com sucesso!")
                time.sleep(2)
            elif escolha == '2':
                print(Cores.AVISO + "\n[*] Executando a ferramenta B...")
                time.sleep(2)
            elif escolha == '3':
                print(Cores.AVISO + "\n[*] Fazendo logout...")
                time.sleep(1)
                return
            else:
                print(Cores.ERRO + "\n[!] Opção inválida.")
                time.sleep(2)
        except KeyboardInterrupt:
            print(Cores.ERRO + "\n\n[!] Logout forçado. Saindo...")
            exit()

def main():
    """Função principal que gerencia o loop do menu, agora corrigida."""
    while True:
        limpar_tela()
        exibir_banner_principal()
        menu_principal()
        
        try:
            escolha = input(f"{Cores.PROMPT}[+] Choose Option: {Cores.INPUT}")
            
            if escolha == '1':
                tela_de_login_servidor()
            elif escolha == '3':
                hwid = get_hwid()
                limpar_tela()
                
                # CORREÇÃO 1: Removida a indentação extra do bloco de texto.
                texto_hwid = f"""
{Cores.TITULO}--- SEU HARDWARE ID (HWID do Disco) ---
{Cores.HWID}{hwid}
{Cores.AVISO}
Este código é enviado para o servidor para verificação.
"""
                exibir_animado(texto_hwid)
                input(f"\n{Cores.PROMPT}Pressione Enter para voltar ao menu...")
            
            elif escolha == '0':
                print(f"{Cores.AVISO}\n[*] Saindo do sistema. Até logo!")
                break
                
            else:
                # CORREÇÃO 2: Adicionado o parêntese final ')' e a mensagem completa.
                print(f"{Cores.ERRO}\n[!] Opção inválida. Tente novamente.")
                time.sleep(1.5) # Pausa para o usuário ler a mensagem.

        except KeyboardInterrupt:
            # Bloco de tratamento de erro para o caso de o usuário pressionar Ctrl+C.
            print(f"{Cores.ERRO}\n\n[!] Operação cancelada. Saindo...")
            break