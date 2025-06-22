import os
import time
import subprocess
import hashlib
import sys
import requests
import base64
from colorama import init, Fore, Style

init(autoreset=True)

# --- CONFIGURAÇÕES ---
VELOCIDADE_LINHA = 0.05
VELOCIDADE_MSG = 0.025

# AQUI VOCÊ DEVE COLAR O HASH GERADO PELO SCRIPT 'gerar_hash.py'
# Se você modificar este arquivo, precisa gerar e colar um novo hash.
HASH_ESPERADO = "1da9c10cdb13a304e733304e47454f586533b20fa72ef6b969e46dc1068155c5"

# --- CLASSE DE CORES ---
class Cores:
    BRIGHT, RESET = Style.BRIGHT, Style.RESET_ALL
    AZUL, AMARELO, VERDE, VERMELHO, BRANCO, MAGENTA = Fore.CYAN + BRIGHT, Fore.YELLOW + BRIGHT, Fore.GREEN + BRIGHT, Fore.RED + BRIGHT, Fore.WHITE + BRIGHT, Fore.MAGENTA + BRIGHT
    BANNER, TITULO, BORDA, TEXTO, DESTAQUE = AZUL, AMARELO, BRANCO, Fore.LIGHTWHITE_EX, MAGENTA
    SUCESSO, ERRO, AVISO, INFO, STATUS = VERDE, VERMELHO, AMARELO, AZUL, BRANCO
    PROMPT, INPUT, HWID = BRANCO, Fore.LIGHTCYAN_EX, AZUL

# --- FUNÇÃO DE SEGURANÇA ---
def verificar_integridade_script():
    """Verifica se o hash do arquivo de script corresponde ao esperado."""
    if HASH_ESPERADO == "COLE_O_SEU_HASH_AQUI":
        print(f"{Cores.AVISO}[AVISO] A verificação de integridade não está configurada.")
        print(f"{Cores.AVISO}Execute o script 'gerar_hash.py' e cole o hash na variável HASH_ESPERADO.")
        time.sleep(4)
        return # Permite a execução para o primeiro teste

    try:
        with open(__file__, 'rb') as f:
            conteudo = f.read()
            hash_atual = hashlib.sha256(conteudo).hexdigest()

        if hash_atual != HASH_ESPERADO:
            # Esta é a mensagem de erro que previne o uso de uma versão modificada
            print(f"{Cores.ERRO}[FATAL] Corrupção de arquivo detectada ou versão adulterada. Encerrando.")
            time.sleep(3)
            os._exit(1)
    except FileNotFoundError:
        print(f"{Cores.ERRO}[FATAL] Arquivo de script não encontrado.")
        time.sleep(2)
        os._exit(1)

# --- FUNÇÕES UTILITÁRIAS E DE INTERFACE (iguais ao original) ---

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
{Cores.STATUS}[i] Security Source    : {Cores.SUCESSO}HWID Lock
{Cores.BORDA}======================================================
"""
    print(Cores.BANNER + banner_arte)

def menu_principal():
    menu_texto = f"""
{Cores.PROMPT}[1] Login
{Cores.PROMPT}[3] {Cores.AVISO}Mostrar meu HWID
{Cores.PROMPT}[0] Exit
    """
    print(menu_texto)

def tela_de_login_servidor():
    URL_CODIFICADA = "aHR0cHM6Ly9tYXJpbi1sb2dpbi1hcGkub25yZW5kZXIuY29t"
    URL_BASE = base64.b64decode(URL_CODIFICADA).decode('utf-8')
    URL_LOGIN = f"{URL_BASE}/api/login"

    limpar_tela()
    exibir_banner_principal()
    print(Cores.TITULO + "--- TELA DE LOGIN (AUTENTICAÇÃO ONLINE) ---\n")

    try:
        usuario_input = input(f"{Cores.PROMPT}[?] Digite seu usuário: {Cores.INPUT}")
        key_input = input(f"{Cores.PROMPT}[?] Digite sua key: {Cores.INPUT}")
        hwid_atual = get_hwid()

        dados_de_login = {"usuario": usuario_input, "key": key_input, "hwid": hwid_atual}
        response = requests.post(URL_LOGIN, json=dados_de_login, timeout=60)

        if response.status_code == 200:
            resposta_json = response.json()
            print(f"\n{Cores.SUCESSO}[SUCCESS] {resposta_json.get('mensagem')}")
            time.sleep(2)
            return usuario_input
        else:
             mensagem_erro = response.json().get("mensagem", "Erro desconhecido.")
             print(f"\n{Cores.ERRO}[ERROR] {mensagem_erro} (Código: {response.status_code})")
             time.sleep(3)
             return None
    except requests.exceptions.RequestException as e:
        print(Cores.ERRO + f"\n[ERROR] A conexão com o servidor falhou: {e}")
        time.sleep(3)
        return None

def tela_logado(nome_usuario):
    # (Esta função permanece idêntica à original)
    limpar_tela()
    print(f"{Cores.SUCESSO}ACESSO AUTORIZADO, BEM-VINDO {nome_usuario}!")
    # ... aqui você colocaria o menu e as funções do seu programa principal
    time.sleep(5)


def main():
    # A verificação agora é a primeira coisa a ser feita
    verificar_integridade_script()

    while True:
        limpar_tela()
        exibir_banner_principal()
        menu_principal()
        escolha = input(f"{Cores.PROMPT}[+] Choose Option: {Cores.INPUT}")

        if escolha == '1':
            usuario_logado = tela_de_login_servidor()
            if usuario_logado:
                tela_logado(usuario_logado)
        elif escolha == '3':
             hwid = get_hwid()
             limpar_tela()
             print(f"{Cores.TITULO}--- SEU HARDWARE ID (HWID do Disco) ---\n{Cores.HWID}{hwid}")
             input(f"\n{Cores.PROMPT}Pressione Enter para voltar ao menu...")
        elif escolha == '0':
            break

if __name__ == "__main__":
    main()