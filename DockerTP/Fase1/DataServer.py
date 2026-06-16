import socket
import json
import os

HOST = '0.0.0.0'
PORT = 8000

def carregar_dados(ficheiro):
    if os.path.exists(ficheiro):
        with open(ficheiro, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return []
    return []

def guardar_dados(ficheiro, dados):
    with open(ficheiro, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4)

def processar_pedido(mensagem):
    try:
        pedido = json.loads(mensagem)
        acao = pedido.get('acao')

        # Rotas puras da Fase 1
        if acao == 'VERIFY_USER':
            users = carregar_dados('users.json')
            credenciais = pedido.get('dados', {})

            email_pedido = credenciais.get('email')
            pass_pedido = credenciais.get('password')

            # O Cofre procura o utilizador sem enviar a lista cá para fora
            for u in users:
                if u.get('email') == email_pedido and u.get('password') == pass_pedido:
                    return json.dumps({"sucesso": True}) # Encontrou!

            # Se o ciclo acabar e não encontrar:
            return json.dumps({"sucesso": False, "erro": "Credenciais inválidas"})

        elif acao == 'ADD_USER':
            users = carregar_dados('users.json')
            users.append(pedido.get('dados'))
            guardar_dados('users.json', users)
            return json.dumps({"sucesso": True})

        elif acao == 'GET_CONTEUDOS':
            return json.dumps(carregar_dados('conteudos.json'))

        elif acao == 'ADD_CONTEUDO':
            conteudos = carregar_dados('conteudos.json')
            conteudos.append(pedido.get('dados'))
            guardar_dados('conteudos.json', conteudos)
            return json.dumps({"sucesso": True})

        elif acao == 'DELETE_CONTEUDO':
            conteudos = carregar_dados('conteudos.json')
            id_apagar = pedido.get('id')
            conteudos = [c for c in conteudos if c.get('id') != id_apagar]
            guardar_dados('conteudos.json', conteudos)
            return json.dumps({"sucesso": True})

        else:
            return json.dumps({"erro": "Ação desconhecida"})

    except Exception as e:
        return json.dumps({"erro": str(e)})

def iniciar_servidor():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[*] DataServer da Fase 1 a escutar em {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            with conn:
                dados = conn.recv(16384) # Buffer grande para aguentar JSONs maiores
                if not dados:
                    break
                resposta = processar_pedido(dados.decode('utf-8'))
                conn.sendall(resposta.encode('utf-8'))

if __name__ == "__main__":
    # Garante que os ficheiros existem para não dar erro na primeira vez
    for ficheiro in ['users.json', 'conteudos.json']:
        if not os.path.exists(ficheiro): guardar_dados(ficheiro, [])

    iniciar_servidor()