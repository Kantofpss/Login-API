# login_system.py - VERSÃO COM CORES CORRIGIDAS

import os
import time
import subprocess
import hashlib
import sys
import requests
from colorama import init, Fore, Style

# Inicializa o Colorama. Essencial para compatibilidade, especialmente no Windows.
init(autoreset=True)

# --- CONFIGURAÇÕES DE VELOCIDADE DA ANIMAÇÃO ---
VELOCIDADE_BANNER = 0.0005
VELOCIDADE_MENU = 0.01
VELOCIDADE_MSG = 0.025
# -------------------------------------------------

# --- 1. CLASSE CENTRAL PARA GERENCIAR CORES ---
class Cores:
    """Classe para centralizar os códigos de cores e estilos do Colorama."""
    # Estilos
    BRIGHT = Style.BRIGHT
    RESET = Style.RESET_ALL
    
    # Cores primárias
    AZUL = Fore.CYAN + BRIGHT
    AMARELO = Fore.YELLOW + BRIGHT
    VERDE = Fore.GREEN + BRIGHT
    VERMELHO = Fore.RED + BRIGHT
    BRANCO = Fore.WHITE + BRIGHT
    MAGENTA = Fore.MAGENTA + BRIGHT
    
    # Elementos da interface
    BANNER = AZUL
    TITULO = AMARELO
    BORDA = BRANCO
    TEXTO = Fore.LIGHTWHITE_EX
    DESTAQUE = MAGENTA
    
    # Estados e feedback
    SUCESSO = VERDE
    ERRO = VERMELHO
    AVISO = AMARELO
    INFO = AZUL
    STATUS = BRANCO
    
    # Inputs e interação
    PROMPT = BRANCO
    INPUT = Fore.LIGHTCYAN_EX
    HWID = AZUL


def escrever_animado(texto, velocidade=VELOCIDADE_MENU):
    """Escreve o texto com um efeito de digitação. Ideal para texto sem cores."""
    for char in texto:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(velocidade)
    if not texto.endswith('\n'):
        print()

def get_hwid():
    """Obtém o número de série do primeiro disco físico (HD/SSD) e o usa como HWID."""
    try:
        comando = 'wmic diskdrive get serialnumber'
        resultado = subprocess.check_output(comando, shell=True, text=True, stderr=subprocess.DEVNULL)
        linhas = resultado.strip().split('\n')
        if len(linhas) > 1:
            hwid_bruto = linhas[1].strip()
        else:
            raise ValueError("Não foi possível obter o serial do disco.")
        hwid_hash = hashlib.sha256(hwid_bruto.encode()).hexdigest()
        return hwid_hash
    except Exception:
        return "ERRO_AO_OBTER_HWID_DISCO"

def limpar_tela():
    """Limpa o console."""
    os.system('cls' if os.name == 'nt' else 'clear')

def exibir_banner_principal():
    """Exibe o banner principal usando as cores centralizadas."""
    banner = r"""

██╗  ██╗███╗   ██╗████████╗███████╗
██║ ██╔╝████╗  ██║╚══██╔══╝╚══███╔╝
█████╔╝ ██╔██╗ ██║   ██║     ███╔╝ 
██╔═██╗ ██║╚██╗██║   ██║    ███╔╝  
██║  ██╗██║ ╚████║   ██║   ███████╗
╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝
                                   
    """
    print(Cores.BANNER + banner)
    print(Cores.BORDA + "======================================================")
    print(f"{Cores.STATUS}[i] Auth System        : {Cores.SUCESSO}Online Server")
    print(f"{Cores.STATUS}[i] Security Source    : {Cores.SUCESSO}HWID")
    print(Cores.BORDA + "======================================================")

def menu_principal():
    """Exibe o menu principal."""
    print(f"{Cores.PROMPT}[1] Login")
    print(f"{Cores.PROMPT}[3] {Cores.AVISO}Mostrar meu HWID")
    print(f"{Cores.PROMPT}[0] Exit")
    print()

def tela_de_login_servidor():
    """
    Função de login que primeiro verifica o status do servidor e depois autentica.
    """
    URL_API = "https://marin-login-api.onrender.com" 

    limpar_tela()
    exibir_banner_principal()
    
    print(Cores.TITULO + "--- TELA DE LOGIN (AUTENTICAÇÃO ONLINE) ---\n")

    try:
        print(f"{Cores.INFO}[*] Verificando o status do servidor...", end="")
        sys.stdout.flush()
        # Aumentamos o timeout aqui também, para o caso da API estar dormindo
        requests.get(URL_API, timeout=45) 
        print(f" {Cores.SUCESSO}Online!")
        time.sleep(1)
    except requests.exceptions.RequestException:
        print(f" {Cores.ERRO}Offline.")
        print(Cores.ERRO + "\n[ERROR] Não foi possível conectar ao servidor de autenticação.")
        time.sleep(3)
        return

    try:
        prompt_usuario = f"{Cores.PROMPT}[?] Digite seu usuário: {Cores.INPUT}"
        usuario_input = input(prompt_usuario)
        
        prompt_key = f"{Cores.PROMPT}[?] Digite sua key: {Cores.INPUT}"
        key_input = input(prompt_key)
        print(Style.RESET_ALL, end="")
        
        hwid_atual = get_hwid()
        if "ERRO" in hwid_atual:
            print(Cores.ERRO + "\n[FATAL] Não foi possível obter um ID de hardware válido do seu PC.")
            time.sleep(3)
            return

        # --- MUDANÇA 1: MENSAGEM DE FEEDBACK MELHORADA ---
        print(Cores.INFO + "\n[*] Autenticando credenciais...")
        print(Cores.AVISO + "(Isso pode levar até um minuto na primeira tentativa do dia)")

        dados_de_login = { "usuario": usuario_input, "key": key_input, "hwid": hwid_atual }
        
        # --- MUDANÇA 2: TIMEOUT AUMENTADO ---
        # Aumentado de 10 para 45 segundos para dar tempo da API na Render "acordar"
        response = requests.post(URL_API, json=dados_de_login, timeout=45)

        if response.status_code == 200:
            resposta_json = response.json()
            if resposta_json.get("status") == "sucesso":
                print(f"{Cores.SUCESSO}\n[SUCCESS] {resposta_json.get('mensagem')}")
                time.sleep(1)
                tela_logado(usuario_input)
            else:
                print(f"{Cores.ERRO}\n[ERROR] {resposta_json.get('mensagem')}")
                time.sleep(3)
        else:
             resposta_json = response.json()
             mensagem_erro = resposta_json.get("mensagem", "Erro desconhecido do servidor.")
             print(f"{Cores.ERRO}\n[ERROR] {mensagem_erro} (Código: {response.status_code})")
             time.sleep(3)

    except requests.exceptions.RequestException:
        # Agora esta mensagem faz mais sentido, pois cobrimos o caso do timeout.
        print(Cores.ERRO + "\n[ERROR] A conexão falhou ou o tempo de espera foi excedido.")
        time.sleep(3)
    except KeyboardInterrupt:
        print(Cores.ERRO + "\n\n[!] Operação cancelada. Saindo...")
        exit()

def tela_logado(nome_usuario):
    """Tela exibida após o login bem-sucedido."""
    while True:
        limpar_tela()
        # --- MUDANÇA: USANDO PRINT() PARA LINHAS COM CORES ---
        print(Cores.SUCESSO + "ACESSO AUTORIZADO\n")
        print(Cores.BORDA + "======================================================\n")
        print(f"{Cores.PROMPT}Bem-vindo, {Cores.INFO}{nome_usuario}{Cores.PROMPT}!")
        print(f"{Cores.TEXTO}Licença vinculada ao HWID: {Cores.SUCESSO}{get_hwid()[:10]}...")
        print(Cores.BORDA + "======================================================\n")
        print(f"{Cores.PROMPT}[1] Ativar Função A")
        print(f"{Cores.PROMPT}[2] Executar Ferramenta B")
        print(f"{Cores.PROMPT}[3] Logout\n")
        
        try:
            prompt_escolha = f"{Cores.PROMPT}[+] Escolha uma opção: {Cores.INPUT}"
            escolha = input(prompt_escolha)
            print(Style.RESET_ALL, end="")
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
    """Função principal que gerencia o loop do menu."""
    while True:
        limpar_tela()
        exibir_banner_principal()
        menu_principal()
        try:
            prompt = f"{Cores.PROMPT}[+] Choose Option: {Cores.INPUT}"
            escolha = input(prompt)
            print(Style.RESET_ALL, end='')

            if escolha == '1':
                tela_de_login_servidor()
            elif escolha == '3':
                hwid = get_hwid()
                limpar_tela()
                print(f"{Cores.TITULO}--- SEU HARDWARE ID (HWID do Disco) ---")
                print(Cores.HWID + hwid)
                print(f"{Cores.AVISO}\nEste código é enviado para o servidor para verificação.")
                input(f"\n{Cores.PROMPT}Pressione Enter para voltar ao menu...")
                print(Style.RESET_ALL, end='')
            elif escolha == '0':
                print(f"{Cores.AVISO}\n[*] Saindo do sistema. Até logo!")
                break
            else:
                print(f"{Cores.ERRO}\n[!] Opção inválida. Tente novamente.")
                time.sleep(1.5)
        except KeyboardInterrupt:
            print(f"{Cores.ERRO}\n\n[!] Operação cancelada. Saindo...")
            break

if __name__ == "__main__":
    main()