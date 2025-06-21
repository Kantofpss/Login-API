import os
import time
import subprocess
import hashlib
import sys
from colorama import init, Fore, Style

# Inicializa o colorama
init(autoreset=True)

# --- CONFIGURAÇÕES DE VELOCIDADE DA ANIMAÇÃO ---
VELOCIDADE_MENU = 0.01     # Rápido para os menus
VELOCIDADE_MSG = 0.025     # Mais lento para mensagens de status
# -------------------------------------------------

# --- BANCO DE DADOS DE USUÁRIOS ---
USUARIOS_AUTORIZADOS = {
    "MarinLove": {
        "key": "157171",
        "hwid": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"  # <-- IMPORTANTE: Edite esta linha!
    }
}
# -----------------------------------

def escrever_animado(texto, velocidade=VELOCIDADE_MENU):
    """
    Função corrigida que exibe texto.
    Imprime a linha inteira de uma vez para garantir que os códigos de cor
    do Colorama funcionem corretamente, e então aplica uma pequena pausa.
    """
    # Imprime o texto completo (com cores) de uma vez só.
    # O flush=True garante que o texto apareça imediatamente.
    print(texto, flush=True)
    
    # Pausa breve para manter o ritmo do programa, substituindo a animação
    # caractere por caractere que estava quebrando as cores.
    time.sleep(velocidade * 5) # Pequena pausa após cada linha

def get_hwid():
    """Obtém o número de série do primeiro disco físico (HD/SSD) e o usa como HWID."""
    try:
        # Comando para Windows Management Instrumentation Command-line (WMIC)
        comando = 'wmic diskdrive get serialnumber'
        resultado = subprocess.check_output(comando, shell=True, text=True, stderr=subprocess.DEVNULL)
        linhas = resultado.strip().split('\n')
        if len(linhas) > 1:
            hwid_bruto = linhas[1].strip()
        else:
            raise ValueError("Não foi possível obter o serial do disco.")
        # Gera um hash seguro do serial para proteger a informação original
        hwid_hash = hashlib.sha256(hwid_bruto.encode()).hexdigest()
        return hwid_hash
    except Exception:
        # Retorno de erro caso o comando wmic falhe (não-Windows, sem permissão, etc.)
        return "ERRO_AO_OBTER_HWID_DISCO"

def limpar_tela():
    """Limpa o console, compatível com Windows (cls) e Linux/Mac (clear)."""
    os.system('cls' if os.name == 'nt' else 'clear')

def exibir_banner_principal():
    """Exibe o banner principal. O título é impresso instantaneamente para agilidade."""
    # ALTERAÇÃO: Adicionada a frase solicitada ao banner.
    banner = r"""
    ██████╗ ██╗ ██████╗   ██████╗██╗  ██╗██████╗ 
    ██╔══██╗██║██╔════╝   ██╔══██╗██║  ██║██╔══██╗
    ██║  ██║██║██║  ███╗  ██████╔╝███████║██║  ██║
    ██║  ██║██║██║   ██║  ██╔══██╗██╔══██║██║  ██║
    ██████╔╝██║╚██████╔╝  ██║  ██║██║  ██║██████╔╝
    ╚═════╝ ╚═╝ ╚═════╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ 
                         suy burru
    """
    print(Fore.CYAN + Style.BRIGHT + banner)
    
    escrever_animado(Fore.WHITE + "======================================================\n", VELOCIDADE_MENU)
    escrever_animado(f"{Style.BRIGHT}[i] Security Source    : {Fore.GREEN}DiskDrive Serial", VELOCIDADE_MSG)
    escrever_animado(f"{Style.BRIGHT}[i] Detection Status   : {Fore.GREEN}UnDetected", VELOCIDADE_MSG)
    escrever_animado(Fore.WHITE + "======================================================\n", VELOCIDADE_MENU)

def menu_principal():
    """Exibe as opções do menu principal."""
    escrever_animado(f"{Style.BRIGHT}[1] Login")
    escrever_animado(f"{Style.BRIGHT}[2] Register (Not Implemented)")
    escrever_animado(f"{Style.BRIGHT}[9] {Fore.YELLOW}Mostrar meu HWID{Style.RESET_ALL}")
    escrever_animado(f"{Style.BRIGHT}[0] Exit")
    print("")

def tela_de_login():
    """Gerencia a interface e a lógica de autenticação do usuário."""
    limpar_tela()
    exibir_banner_principal()
    escrever_animado(Fore.YELLOW + Style.BRIGHT + "--- TELA DE LOGIN (HWID PROTECTED) ---")
    
    try:
        print(Fore.YELLOW + f"[?] Digite seu usuário: ", end='')
        usuario_input = input()
        
        print(Fore.YELLOW + f"[?] Digite sua key: ", end='')
        key_input = input()
        
        hwid_atual = get_hwid()

        if usuario_input in USUARIOS_AUTORIZADOS:
            usuario_db = USUARIOS_AUTORIZADOS[usuario_input]
            if key_input == usuario_db["key"]:
                if hwid_atual == usuario_db["hwid"]:
                    escrever_animado(Fore.GREEN + "\n[SUCCESS] Login bem-sucedido! Hardware verificado.", VELOCIDADE_MSG)
                    time.sleep(1)
                    tela_logado(usuario_input)
                    return True
                else:
                    escrever_animado(Fore.RED + "\n[ERROR] Falha na autenticação de Hardware (HWID).", VELOCIDADE_MSG)
                    escrever_animado(Fore.CYAN + f"    -> Seu HWID (baseado no disco): {hwid_atual}", VELOCIDADE_MSG)
                    escrever_animado(Fore.YELLOW +  "    -> Este login está registrado para outro PC.", VELOCIDADE_MSG)
                    time.sleep(3)
            else:
                escrever_animado(Fore.RED + "\n[ERROR] Key (senha) incorreta.", VELOCIDADE_MSG)
                time.sleep(2)
        else:
            escrever_animado(Fore.RED + "\n[ERROR] Usuário não encontrado.", VELOCIDADE_MSG)
            time.sleep(2)

    except KeyboardInterrupt:
        print(Fore.RED + "\n\n[!] Operação cancelada. Saindo...")
        exit()
    
    return False

def tela_logado(nome_usuario):
    """Exibe a tela pós-login com opções para o usuário autenticado."""
    while True:
        limpar_tela()
        escrever_animado(Fore.GREEN + Style.BRIGHT + "ACESSO AUTORIZADO", VELOCIDADE_MENU)
        escrever_animado(Fore.WHITE + "======================================================", VELOCIDADE_MENU)
        escrever_animado(f"{Style.BRIGHT}Bem-vindo, {Fore.CYAN}{nome_usuario}{Style.RESET_ALL}{Style.BRIGHT}!", VELOCIDADE_MSG)
        escrever_animado(f"{Style.BRIGHT}Licença vinculada ao HWID: {Fore.GREEN}{get_hwid()[:10]}...", VELOCIDADE_MSG)
        escrever_animado(Fore.WHITE + "======================================================", VELOCIDADE_MENU)
        escrever_animado(f"{Style.BRIGHT}[1] Ativar Função A")
        escrever_animado(f"{Style.BRIGHT}[2] Executar Ferramenta B")
        escrever_animado(f"{Style.BRIGHT}[3] Logout\n")
        
        try:
            print(Fore.YELLOW + f"[+] Escolha uma opção: ", end='')
            escolha = input()

            if escolha == '1':
                escrever_animado(Fore.GREEN + "\n[+] Função A ativada com sucesso!", VELOCIDADE_MSG)
                time.sleep(2)
            elif escolha == '2':
                escrever_animado(Fore.YELLOW + "\n[*] Executando a ferramenta B...", VELOCIDADE_MSG)
                time.sleep(2)
            elif escolha == '3':
                escrever_animado(Fore.YELLOW + "\n[*] Fazendo logout...", VELOCIDADE_MSG)
                time.sleep(1)
                return
            else:
                escrever_animado(Fore.RED + "\n[!] Opção inválida.", VELOCIDADE_MSG)
                time.sleep(2)
        except KeyboardInterrupt:
            print(Fore.RED + "\n\n[!] Logout forçado. Saindo...")
            exit()

def main():
    """Função principal que executa o loop do menu."""
    while True:
        limpar_tela()
        exibir_banner_principal()
        menu_principal()
        try:
            print(Fore.YELLOW + Style.BRIGHT + "[+] Choose Option: ", end='')
            escolha = input()

            if escolha == '1':
                tela_de_login()
            elif escolha == '2':
                escrever_animado(Fore.YELLOW + "\n[!] A função de registro ainda não foi implementada.", VELOCIDADE_MSG)
                time.sleep(2)
            elif escolha == '9':
                hwid = get_hwid()
                limpar_tela()
                escrever_animado(Fore.YELLOW + Style.BRIGHT + "\n--- SEU HARDWARE ID (HWID do Disco) ---", VELOCIDADE_MSG)
                print(Fore.CYAN + Style.BRIGHT + hwid)
                escrever_animado(Fore.YELLOW + "\nCopie o código acima e cole no script para registrar sua máquina.", VELOCIDADE_MSG)
                input("\nPressione Enter para voltar ao menu...")
            elif escolha == '0':
                escrever_animado(Fore.YELLOW + "\n[*] Saindo do sistema. Até logo!", VELOCIDADE_MSG)
                break
            else:
                escrever_animado(Fore.RED + "\n[!] Opção inválida. Tente novamente.", VELOCIDADE_MSG)
                time.sleep(1.5)
        except KeyboardInterrupt:
            print(Fore.RED + "\n\n[!] Operação cancelada. Saindo...")
            break

if __name__ == "__main__":
    main()