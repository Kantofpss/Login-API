# login_system.py - VERSÃO COM TRAVA DE HWID E PROTEÇÃO ANTI-CRACKING (SEM HASH DE ARQUIVO)

import os
import time
import subprocess
import hashlib
import sys
import requests
import base64
from colorama import init, Fore, Style

# Inicializa o Colorama
init(autoreset=True)

# --- CONFIGURAÇÕES DE VELOCIDADE DA ANIMAÇÃO ---
VELOCIDADE_LINHA = 0.05
VELOCIDADE_MSG = 0.025
# -------------------------------------------------

# --- CLASSE DE CORES ---
class Cores:
    BRIGHT, RESET = Style.BRIGHT, Style.RESET_ALL
    AZUL, AMARELO, VERDE, VERMELHO, BRANCO, MAGENTA = Fore.CYAN + BRIGHT, Fore.YELLOW + BRIGHT, Fore.GREEN + BRIGHT, Fore.RED + BRIGHT, Fore.WHITE + BRIGHT, Fore.MAGENTA + BRIGHT
    BANNER, TITULO, BORDA, TEXTO, DESTAQUE = AZUL, AMARELO, BRANCO, Fore.LIGHTWHITE_EX, MAGENTA
    SUCESSO, ERRO, AVISO, INFO, STATUS = VERDE, VERMELHO, AMARELO, AZUL, BRANCO
    PROMPT, INPUT, HWID = BRANCO, Fore.LIGHTCYAN_EX, AZUL

# --- FUNÇÕES DE SEGURANÇA (ANTI-CRACKING) ---

# NOVO: Hash esperado para o bytecode da função de login.
# Gerado com: hashlib.sha256(tela_de_login_servidor.__code__.co_code).hexdigest()
HASH_FUNCAO_LOGIN = "d010e051d3b0748b9f1d86d99b1a0e10b0a21f8a851163af9809989679f1cf44" # Este hash precisa ser atualizado se a função mudar!

def verificar_ambiente():
    """Verifica condições de debugger e integridade de funções críticas."""
    # 1. Detecção de Debugger por Rastreamento
    if sys.gettrace() is not None:
        print(f"{Cores.ERRO}[FATAL] Debugger detectado (trace). Encerrando.")
        time.sleep(2)
        os._exit(1)

    # 2. Detecção de Debugger por Tempo de Execução
    start_time = time.perf_counter()
    time.sleep(0.1) # Uma operação que deveria ser muito rápida
    end_time = time.perf_counter()
    if (end_time - start_time) > 0.5: # Se demorou mais de 0.5s, algo está muito errado
        print(f"{Cores.ERRO}[FATAL] Debugger detectado (timing). Encerrando.")
        time.sleep(2)
        os._exit(1)

    # 3. Verificação de Integridade da Função de Login
    try:
        # ATENÇÃO: Se você alterar a função 'tela_de_login_servidor',
        # você PRECISA recalcular este hash e atualizar a constante HASH_FUNCAO_LOGIN.
        # Use o seguinte código para gerar o novo hash:
        # import hashlib
        # print(hashlib.sha256(tela_de_login_servidor.__code__.co_code).hexdigest())
        hash_atual_funcao = hashlib.sha256(tela_de_login_servidor.__code__.co_code).hexdigest()
        if hash_atual_funcao != HASH_FUNCAO_LOGIN:
            print(f"{Cores.ERRO}[FATAL] Corrupção de função crítica detectada. Encerrando.")
            time.sleep(2)
            os._exit(1)
    except Exception:
        os._exit(1) # Falha silenciosa se não conseguir checar

# --- FUNÇÕES UTILITÁRIAS ---

def exibir_animado(texto_multilinha, velocidade=VELOCIDADE_LINHA):
    for linha in texto_multilinha.strip().split('\n'):
        print(linha)
        time.sleep(velocidade)

def get_hwid():
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

# --- FUNÇÕES DE INTERFACE ---

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
{Cores.STATUS}[i] Security Source    : {Cores.SUCESSO}HWID Lock & Challenge
{Cores.BORDA}======================================================
"""
    print(Cores.BANNER + banner_arte)
    exibir_animado(info, 0.1)

def menu_principal():
    menu_texto = f"""
{Cores.PROMPT}[1] Login
{Cores.PROMPT}[3] {Cores.AVISO}Mostrar meu HWID
{Cores.PROMPT}[0] Exit
    """
    exibir_animado(menu_texto)

def tela_de_login_servidor():
    """Função de login que implementa o fluxo de Challenge-Response."""
    verificar_ambiente() # Checagem extra de segurança

    URL_CODIFICADA = "aHR0cHM6Ly9tYXJpbi1sb2dpbi1hcGkub25yZW5kZXIuY29t" # Mantenha a sua URL
    URL_BASE = base64.b64decode(URL_CODIFICADA).decode('utf-8')
    URL_REQUEST_CHALLENGE = f"{URL_BASE}/api/request-challenge"
    URL_VALIDATE_RESPONSE = f"{URL_BASE}/api/validate-response"

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
        return None

    try:
        usuario_input = input(f"{Cores.PROMPT}[?] Digite seu usuário: {Cores.INPUT}")
        key_input = input(f"{Cores.PROMPT}[?] Digite sua key: {Cores.INPUT}")
        hwid_atual = get_hwid()

        if "ERRO" in hwid_atual:
            print(Cores.ERRO + "\n[FATAL] Não foi possível obter um ID de hardware válido.")
            time.sleep(3)
            return None

        # ETAPA 1: Solicitar o desafio (challenge) ao servidor
        print(Cores.INFO + "\n[1/2] Solicitando autorização inicial...")
        dados_iniciais = {"usuario": usuario_input, "key": key_input}
        response = requests.post(URL_REQUEST_CHALLENGE, json=dados_iniciais, timeout=60)

        if response.status_code != 200:
            mensagem_erro = response.json().get("mensagem", "Erro desconhecido.")
            print(f"\n{Cores.ERRO}[ERROR] {mensagem_erro} (Código: {response.status_code})")
            time.sleep(3)
            return None

        challenge = response.json().get("challenge")
        if not challenge:
            print(f"\n{Cores.ERRO}[ERROR] Falha ao receber o desafio de segurança do servidor.")
            time.sleep(3)
            return None

        # ETAPA 2: Calcular a resposta e enviá-la para validação
        print(f"{Cores.INFO}[2/2] Validando sessão segura...")
        
        # LÓGICA CRÍTICA: O cliente calcula a resposta.
        # O cracker precisa descobrir e replicar isso.
        resposta_calculada = hashlib.sha256(f"{challenge}-{hwid_atual}".encode()).hexdigest()
        
        dados_de_validacao = {"usuario": usuario_input, "hwid": hwid_atual, "response": resposta_calculada}
        response_final = requests.post(URL_VALIDATE_RESPONSE, json=dados_de_validacao, timeout=60)

        if response_final.status_code == 200:
            resposta_json = response_final.json()
            if resposta_json.get("status") == "sucesso":
                print(f"\n{Cores.SUCESSO}[SUCCESS] {resposta_json.get('mensagem')}")
                time.sleep(2)
                return usuario_input # SUCESSO!
            else: # Este 'else' não deveria acontecer com status 200, mas é uma segurança
                print(f"\n{Cores.ERRO}[ERROR] {resposta_json.get('mensagem')}")
                time.sleep(3)
                return None
        else:
             mensagem_erro = response_final.json().get("mensagem", "Erro desconhecido.")
             print(f"\n{Cores.ERRO}[ERROR] {mensagem_erro} (Código: {response_final.status_code})")
             time.sleep(3)
             return None

    except requests.exceptions.RequestException:
        print(Cores.ERRO + "\n[ERROR] A conexão falhou ou o tempo de espera foi excedido.")
        time.sleep(3)
        return None
    except KeyboardInterrupt:
        print(Cores.ERRO + "\n\n[!] Operação cancelada. Saindo...")
        exit()
    except Exception:
        print(Cores.ERRO + "\n\n[!] Ocorreu um erro inesperado durante o login.")
        time.sleep(2)
        return None

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
    """Função principal que gerencia o loop do menu."""
    verificar_ambiente() # Executa as verificações de segurança na inicialização

    while True:
        limpar_tela()
        exibir_banner_principal()
        menu_principal()
        try:
            escolha = input(f"{Cores.PROMPT}[+] Choose Option: {Cores.INPUT}")
            if escolha == '1':
                usuario_logado = tela_de_login_servidor()
                if usuario_logado:
                    tela_logado(usuario_logado)
            elif escolha == '3':
                hwid = get_hwid()
                limpar_tela()
                texto_hwid = f"""
{Cores.TITULO}--- SEU HARDWARE ID (HWID do Disco) ---
{Cores.HWID}{hwid}
{Cores.AVISO}
Este código é enviado para o servidor para verificação.
Se esta é sua primeira vez logando, seu HWID será registrado.
"""
                exibir_animado(texto_hwid)
                input(f"\n{Cores.PROMPT}Pressione Enter para voltar ao menu...")
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