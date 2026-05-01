import socket
import json
import os

# Configuração de caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRIVATE_DIR = os.path.join(BASE_DIR, "dados_privados")

if not os.path.exists(PRIVATE_DIR):
    os.makedirs(PRIVATE_DIR)

def iniciar_servidor():
    host = '0.0.0.0'
    port = 8000

    # Inicializa o socket TCP
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Permite reutilizar a porta imediatamente após restart
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    servidor.bind((host, port))
    servidor.listen(5) 
    
    print(f"[*] Servidor de Dados TCP a escutar na porta {port}...")

    while True:
        cliente, endereco = servidor.accept()
        
        try:
            # Recebe o request (limite de 1MB para suportar JSONs grandes)
            dados_recebidos = cliente.recv(1048576).decode('utf-8')
            
            if not dados_recebidos:
                cliente.close()
                continue

            # Parse do protocolo customizado: COMANDO|FICHEIRO|DADOS
            partes = dados_recebidos.split("|", 2)
            comando = partes[0]
            ficheiro = partes[1]
            caminho = os.path.join(PRIVATE_DIR, ficheiro)

            if comando == "GET":
                try:
                    with open(caminho, "r", encoding="utf-8") as f:
                        conteudo_texto = f.read()
                except FileNotFoundError:
                    conteudo_texto = "[]" 
                
                cliente.sendall(conteudo_texto.encode('utf-8'))

            elif comando == "POST":
                dados_json_texto = partes[2] 
                dados_python = json.loads(dados_json_texto)
                
                with open(caminho, "w", encoding="utf-8") as f:
                    json.dump(dados_python, f, indent=4)
                
                cliente.sendall("SUCESSO".encode('utf-8'))

        except Exception as e:
            print(f"[-] Erro interno no DataServer: {e}")
            cliente.sendall("ERRO".encode('utf-8'))
        
        finally:
            cliente.close()

if __name__ == "__main__":
    iniciar_servidor()