import os
import json
import uuid
import socket  
import time    
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session

# diretorio base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

# configs
app.config["SECRET_KEY"] = "chave_projeto_2025"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # limite 500mb

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# sistema de traducoes
def carregar_traducoes():
    try:
        with open(os.path.join(BASE_DIR, "private", "traducoes.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# injetar traducoes nos templates
@app.context_processor
def injetar_tradutor():
    dicionario = carregar_traducoes()
    def traducoes(key):
        lang = session.get("lang", "pt")
        # tenta buscar na lingua certa, senao vai ao pt
        return dicionario.get(lang, dicionario.get("pt", {})).get(key, key)
    return dict(traducoes=traducoes, lang=session.get("lang", "pt"))

# rota para mudar lingua
@app.route("/lang/<lang>")
def change_language(lang):
    if lang in ["pt", "en"]:
        session["lang"] = lang
    return redirect(request.referrer or url_for("index"))


Session(app)


def load_data(filename):
    """Lê dados enviando um comando GET via Socket."""
    host = "servidor_dados"
    port = 8000
    
    try:
        # 1. Cria o telefone e liga
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((host, port))
        
        # 2. Constrói a mensagem: "GET|users.json"
        mensagem = f"GET|{filename}"
        
        # 3. Envia (codificado em bytes)
        s.sendall(mensagem.encode('utf-8'))
        
        # 4. Fica à espera da resposta (tamanho grande para JSONs compridos)
        resposta_bytes = s.recv(1048576)
        s.close()
        
        # 5. Descodifica a resposta e transforma o texto num dicionário Python
        texto = resposta_bytes.decode('utf-8')
        return json.loads(texto)
        
    except (socket.timeout, ConnectionRefusedError):
        print("ERRO: Contentor de Dados offline (Socket).")
        return None # Mantemos o None para o nosso sistema de erro de Login funcionar!
    except Exception as e:
        print(f"Erro ao ligar à BD por Socket: {e}")
        return []

def save_data(filename, data):
    """Guarda dados enviando um comando POST via Socket."""
    host = "servidor_dados"
    port = 8000
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((host, port))
        
        # 1. Transforma o Dicionário Python (data) num texto formatado (JSON string)
        json_texto = json.dumps(data)
        
        # 2. Constrói a mensagem: "POST|users.json|[{...}]"
        mensagem = f"POST|{filename}|{json_texto}"
        
        # 3. Envia o pacote todo
        s.sendall(mensagem.encode('utf-8'))
        
        # 4. Espera só pelo recibo (ex: "SUCESSO")
        recibo = s.recv(1024).decode('utf-8')
        s.close()
        
        if recibo == "SUCESSO":
            return True
        return False
        
    except Exception as e:
        print(f"Erro ao guardar na BD por Socket: {e}")
        return False
        
def aguardar_servidor_dados():
    host = "servidor_dados"
    port = 8000
    tentativas_maximas = 10
    
    print(f"[*] A iniciar o Handshake via Socket com {host}:{port}...")
    
    for tentativa in range(1, tentativas_maximas + 1):
        try:
            # 1. Cria um socket TCP (como um telefone analógico)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2) # Espera no máximo 2 segundos por resposta
            
            # 2. Tenta ligar à porta
            s.connect((host, port))
            
            # 3. Se não deu erro a ligar, é porque o outro lado atendeu!
            print(f"[+] Sucesso! O servidor_dados respondeu via Socket à tentativa {tentativa}.")
            s.close() # Desliga o telefone
            return True
            
        except (socket.timeout, ConnectionRefusedError, socket.gaierror):
            # Se deu erro, o DataServer ainda está a arrancar ou desligado
            print(f"[-] Tentativa {tentativa}/{tentativas_maximas} falhou. A aguardar 3 segundos...")
            s.close()
            time.sleep(3) # Espera 3 segundos antes de tentar de novo
            
    print("O servidor_dados não acordou a tempo. A arrancar a Web na mesma (com aviso).")
    return False

# --- rotas ---

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        users = load_data("users.json")
        if users is None:
            return render_template("formLoginT.html", erro="msg_db_offline")
        for u in users:
            if u['email'] == email and u['password'] == password:
                session['user'] = email
                # default pt se nao existir
                if "lang" not in session: session["lang"] = "pt"
                return redirect(url_for('index'))
        
        # correcao: mandar a chave do erro para ser traduzida
        return render_template("formLoginT.html", erro="msg_dados_invalidos")
        
    return render_template("formLoginT.html")

@app.route("/registo", methods=["GET", "POST"])
def registo():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        users = load_data("users.json")
        users.append({"email": email, "password": password})
        save_data("users.json", users)
        return redirect(url_for("login"))
    return render_template("formRegistro.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    if not session.get("user"): return redirect(url_for("login"))
    
    todas = load_data("conteudos.json")
    minhas = []
    
    for m in todas:
        if m['autor'] == session['user']:
            minhas.append(m)
    
    query = request.args.get('q')
    resultados = []
    
    if query:
        query = query.lower()
        for m in minhas:
            if query in m['titulo'].lower() or query in m['descricao'].lower():
                resultados.append(m)
    else:
        resultados = minhas

    return render_template("index.html", memorias=resultados, query=query)

@app.route("/adicionar", methods=["GET", "POST"])
def adicionar():
    if not session.get("user"): return redirect(url_for("login"))

    if request.method == "POST":
        arquivo = request.files.get('ficheiro')
        nome_ficheiro = ""
        
        if arquivo:
            ext = os.path.splitext(arquivo.filename)[1].lower()
            nome_ficheiro = str(uuid.uuid4()) + ext
            arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_ficheiro))
        
        nova = {
            "id": str(uuid.uuid4()),
            "autor": session['user'],
            "titulo": request.form.get("titulo"),
            "descricao": request.form.get("descricao"),
            "tipo": request.form.get("tipo"),
            "ficheiro": nome_ficheiro,
            "lat": request.form.get("latitude"),
            "lon": request.form.get("longitude")
        }
        
        dados = load_data("conteudos.json")
        dados.append(nova)
        save_data("conteudos.json", dados)
        return redirect(url_for("index"))

    return render_template("form_post.html")

@app.route("/editar/<id_memoria>", methods=["GET", "POST"])
def editar(id_memoria):
    if not session.get("user"): return redirect(url_for("login"))
    
    dados = load_data("conteudos.json")
    memoria_alvo = None
    for m in dados:
        if m['id'] == id_memoria:
            memoria_alvo = m
            break
            
    if not memoria_alvo: return redirect(url_for("index"))

    if request.method == "POST":
        memoria_alvo['titulo'] = request.form.get("titulo")
        memoria_alvo['descricao'] = request.form.get("descricao")
        memoria_alvo['tipo'] = request.form.get("tipo")
        memoria_alvo['lat'] = request.form.get("latitude")
        memoria_alvo['lon'] = request.form.get("longitude")
        
        arquivo = request.files.get('ficheiro')
        if arquivo and arquivo.filename != "":
            try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], memoria_alvo['ficheiro']))
            except: pass
            
            ext = os.path.splitext(arquivo.filename)[1].lower()
            novo = str(uuid.uuid4()) + ext
            arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], novo))
            memoria_alvo['ficheiro'] = novo
            
        save_data("conteudos.json", dados)
        return redirect(url_for("index"))

    return render_template("form_post.html", memoria=memoria_alvo)

@app.route("/apagar/<id_memoria>", methods=["GET", "DELETE"])
def apagar(id_memoria):
    if not session.get("user"): 
        if request.method == 'DELETE': return {"erro": "Não autorizado"}, 401
        return redirect(url_for("login"))
    
    dados = load_data("conteudos.json")
    nova_lista = []
    
    for m in dados:
        if m['id'] != id_memoria:
            nova_lista.append(m)
        else:
            # apagar ficheiro fisico
            if m.get('ficheiro'):
                try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], m['ficheiro']))
                except: pass
            
    save_data("conteudos.json", nova_lista)
    
    if request.method == 'DELETE':
        return {"sucesso": True}

    return redirect(url_for("index"))

if __name__ == "__main__":
    # socket
    aguardar_servidor_dados()
    
    app.run(host="0.0.0.0", port=5000, debug=True)