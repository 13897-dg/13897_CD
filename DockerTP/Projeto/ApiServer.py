from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras
import os
import time

app = Flask(__name__)

# 1. Configuração da Base de Dados usando as Variáveis do Docker
DB_HOST = os.environ.get("DB_HOST", "base_dados")
DB_USER = os.environ.get("DB_USER", "david")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "secreto")
DB_NAME = os.environ.get("DB_NAME", "memorias_db")

def get_db_connection():
    """Tenta estabelecer ligação. Como a BD demora uns segundos a arrancar,
       fazemos um mini 'handshake' com tentativas."""
    tentativas = 5
    for i in range(tentativas):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                dbname=DB_NAME
            )
            return conn
        except Exception as e:
            print(f"[-] A aguardar Base de Dados... tentativa {i+1}/{tentativas}")
            time.sleep(3)
    raise Exception("Não foi possível ligar à Base de Dados PostgreSQL.")

def init_db():
    """Cria as tabelas oficiais se elas não existirem. Adeus JSONs!"""
    conn = get_db_connection()
    cur = conn.cursor()

    # Tabela de Utilizadores
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email VARCHAR(255) PRIMARY KEY,
            password VARCHAR(255) NOT NULL
        )
    ''')

    # Tabela de Memórias (Conteúdos)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS conteudos (
            id VARCHAR(100) PRIMARY KEY,
            autor VARCHAR(255) REFERENCES users(email),
            titulo VARCHAR(255),
            descricao TEXT,
            tipo VARCHAR(50),
            ficheiro VARCHAR(255),
            lat VARCHAR(50),
            lon VARCHAR(50)
        )
    ''')

    conn.commit()
    cur.close()
    conn.close()

# --- AS ROTAS DA NOSSA API REST ---

@app.route('/api/auth', methods=['POST'])
def auth():
    """Recebe email e password e confirma na BD."""
    dados = request.json
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # O SQL protege contra injecções passando os parâmetros à parte (%s)
    cur.execute('SELECT * FROM users WHERE email = %s AND password = %s', (dados['email'], dados['password']))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if user:
        return jsonify({"status": "VALIDO"}), 200
    return jsonify({"status": "INVALIDO"}), 401

@app.route('/api/users', methods=['POST'])
def registar_user():
    """Regista um novo utilizador."""
    dados = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO users (email, password) VALUES (%s, %s)', (dados['email'], dados['password']))
        conn.commit()
        sucesso = True
    except psycopg2.IntegrityError:
        # Se o email já existir (Chave Primária), o Postgres dá erro de integridade
        sucesso = False
    finally:
        cur.close()
        conn.close()

    if sucesso:
        return jsonify({"status": "SUCESSO"}), 201
    return jsonify({"status": "ERRO"}), 400

@app.route('/api/conteudos', methods=['GET', 'POST'])
def gerir_conteudos():
    """Lê todas as memórias ou adiciona uma nova."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    if request.method == 'GET':
        cur.execute('SELECT * FROM conteudos')
        memorias = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(memorias), 200

    if request.method == 'POST':
        dados = request.json
        cur.execute('''
            INSERT INTO conteudos (id, autor, titulo, descricao, tipo, ficheiro, lat, lon)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (dados['id'], dados['autor'], dados['titulo'], dados['descricao'], dados['tipo'], dados['ficheiro'], dados['lat'], dados['lon']))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "SUCESSO"}), 201

@app.route('/api/conteudos/<id_memoria>', methods=['PUT', 'DELETE'])
def alterar_conteudo(id_memoria):
    """Atualiza ou apaga uma memória específica."""
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'PUT':
        dados = request.json
        cur.execute('''
            UPDATE conteudos 
            SET titulo=%s, descricao=%s, tipo=%s, ficheiro=%s, lat=%s, lon=%s
            WHERE id=%s
        ''', (dados['titulo'], dados['descricao'], dados['tipo'], dados['ficheiro'], dados['lat'], dados['lon'], id_memoria))
        conn.commit()

    elif request.method == 'DELETE':
        cur.execute('DELETE FROM conteudos WHERE id=%s', (id_memoria,))
        conn.commit()

    cur.close()
    conn.close()
    return jsonify({"status": "SUCESSO"}), 200

if __name__ == '__main__':
    print("[*] A inicializar tabelas na Base de Dados PostgreSQL...")
    init_db()
    print("[*] API REST pronta e à escuta na porta 8000...")
    app.run(host='0.0.0.0', port=8000)