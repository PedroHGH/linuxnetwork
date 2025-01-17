import re
import psutil
import socket
import subprocess
import ipaddress

#funcao para logar o usuario com login e senha fixos
def login():

    print('Insira seu login e senha:')

    while True:

        usuario = input('Seu login:')
        senha = input('Sua senha:')

        if usuario == 'user' and senha == 'senha':
            
            return True
        
        else:

            print('Dados inválidos')

#validacao de ip com regex e verificacao se nenhum dos bytes/octetos estão fora da range de 0 a 255
def validarIP(entrada):

    if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}/([0-9]|[12][0-9]|3[0-2])$", entrada):


        ipmascara = entrada.split("/")
        ip = ipmascara[0]
        mascara = ipmascara[1]

        bytes = ip.split(".")



        if all(0 <= int(byte) <= 255 for byte in bytes):
            
            return True
        
        else:

            print("IP inválido: Pelo menos um dos bytes é menor que 0 ou maior que 255")
        
    else:

        print("IP inválido: Fora do padrão")
    
    return False

#configuracao das interfaces com subprocess.run para rodar os comandos 
def configurarInterface(interface, ipcommascara):

    if not validarIP(ipcommascara):

        return

    try:

        interfaces = psutil.net_if_addrs()

        if interface not in interfaces:

            print("Erro: A interface inserida não existe.")
            return

        subprocess.run(["sudo", "ip", "addr", "add", ipcommascara, "dev", interface], check=True)
      
        print(f"IP {ipcommascara} configurado com sucesso na interface {interface}.")
   
    except subprocess.CalledProcessError:

        print("Erro: Falha ao configurar o IP. Verifique suas permissões.")

#mostrando as interfaces e seus atributos a partir dos dados obtidos com a psutil e socket
def mostrarInterfaces():

    interfaces = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    print(f"{'Interface':<20} {'Endereço IP':<20} {'MAC':<20} {'MTU':<20} {'Status':<20}")

    for nome, addrs in sorted(interfaces.items()):

        status = "UP" if stats[nome].isup else "DOWN"
        mtu = stats[nome].mtu
        ipv4s = []
        mac = None

        for addr in addrs:

            if addr.family == socket.AF_INET:

                net = ipaddress.IPv4Network(f"{addr.address}/{addr.netmask}", strict=False)

                ipv4s.append(f"{addr.address}/{net.prefixlen}")

            elif addr.family == socket.AF_PACKET:

                mac = addr.address
        
        if ipv4s:

            for i, ip in enumerate(ipv4s):

                if i == 0:

                    print(f"{nome:<20} {ip:<20} {mac or 'Vazio':<20} {mtu:<20} {status:<20}")

                else:

                    print(f"{'':<20} {ip:<20}")

        else:

            print(f"{nome:<20} {'Vazio':<20} {mac or 'Vazio':<20} {mtu:<20} {status:<20}")
                
#funcao main com as chamadas para outras funções
def main():

    print("Bem vindo ao sistema de configuração de rede")

    while True:

        comando = input("> ").strip()

        if comando.startswith("configurar"):

            divisoes = comando.split()

            if len(divisoes) == 4:

                if divisoes[2] == "como":

                    configurarInterface(divisoes[1], divisoes[3])
                
                else:

                    print("O comando configurar deve estar escrito no formato: configurar<interface> como <ip/mascara>")

        elif comando=="mostrar interfaces":

            mostrarInterfaces()

        elif comando == "sair":

            print("Saindo...")

            break
            
        else:

            print("Comando inválido. Os comandos aceitos são:")
            print("configurar<interface> como <ip/mascara>")
            print("mostrar interfaces")
            print("sair")

if __name__ == "__main__":

    if login():

        main()

    else:

        print("Saindo do sistema")