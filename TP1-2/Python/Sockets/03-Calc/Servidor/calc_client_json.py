import socket
import json

def cliente_calculadora():
    port = 12350
    host = "localhost"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            print("--- Calculadora de Números Complexos ---")
            
            # Pedir dados ao utilizador
            op = input("Operação (soma, subtracao, multiplicacao): ").lower()
            r1 = float(input("Número 1 - Parte Real: "))
            i1 = float(input("Número 1 - Parte Imaginária: "))
            r2 = float(input("Número 2 - Parte Real: "))
            i2 = float(input("Número 2 - Parte Imaginária: "))

            # Criar o dicionário JSON (Heterogeneidade resolvida via texto)
            pedido = {
                "op": op,
                "r1": r1, "i1": i1,
                "r2": r2, "i2": i2
            }

            # Enviar dados
            s.sendall(json.dumps(pedido).encode("utf-8"))

            # Receber e processar resposta
            data = s.recv(1024).decode("utf-8")
            res = json.loads(data)
            
            print(f"\nResultado do Servidor: {res['res_real']} + {res['res_imag']}j")

        except Exception as e:
            print(f"Erro no cliente: {e}")

if __name__ == "__main__":
    cliente_calculadora()