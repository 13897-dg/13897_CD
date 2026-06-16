import os
import json
import uuid
import socket
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = "chave_projeto_2025"
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, 'static', 'uploads')

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

Session(app)

# O endereço do contentor do DataServer (definido no docker-compose)
DATA_HOST = 'data_app'
DATA_PORT = 8000

# --- A MÁQUINA DE SOCKETS (Cumprimento da Fase 1) ---
def enviar_socket(pedido):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((DATA_HOST, DATA_PORT))
            s.sendall(json.dumps(pedido).encode('utf-8'))
            resposta = s.recv(16384)
            return json.loads(resposta.decode('utf-8'))
    except Exception as e:
        print(f"Erro na ligação por socket ao DataServer: {e}")
        return None

# --- SISTEMA DE TRADUÇÕES ---
def carregar_traducoes():
    try:
        with open(os.path.join(BASE_DIR, "private", "traducoes.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

@app.context_processor
def injetar_tradutor():
    dicionario = carregar_traducoes()
    def traducoes(key):
        lang = session.get("lang", "pt")
        return dicionario.get(lang, dicionario.get("pt", {})).get(key, key)
    return dict(traducoes=traducoes, lang=session.get("lang", "pt"))

@app.route("/lang/<lang>")
def change_language(lang):
    if lang in ["pt", "en"]:
        session["lang"] = lang
    return redirect(request.referrer or url_for("index"))

# --- ROTAS ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # 1. Pede a verificação ao Cofre
        resposta = enviar_socket({
            "acao": "VERIFY_USER",
            "dados": {"email": email, "password": password}
        })

        # 2. Se a resposta for None, o cabo de rede está cortado (DataServer desligado)
        if resposta is None:
            return render_template("formLoginT.html", erro="msg_db_offline")

        # 3. Se respondeu com sucesso
        if resposta.get("sucesso") == True:
            session['user'] = email
            if "lang" not in session: session["lang"] = "pt"
            return redirect(url_for('index'))
        else:
            # 4. Se respondeu sem sucesso, a culpa é do email/pass
            return render_template("formLoginT.html", erro="msg_dados_invalidos")

    return render_template("formLoginT.html")

@app.route("/registo", methods=["GET", "POST"])
def registo():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        enviar_socket({"acao": "ADD_USER", "dados": {"email": email, "password": password}})
        return redirect(url_for("login"))

    return render_template("formRegistro.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    if not session.get("user"): return redirect(url_for("login"))

    todas = enviar_socket({"acao": "GET_CONTEUDOS"}) or []
    minhas = [m for m in todas if m.get('autor') == session['user']]

    query = request.args.get('q')
    if query:
        query = query.lower()
        minhas = [m for m in minhas if query in m.get('titulo', '').lower() or query in m.get('descricao', '').lower()]

    return render_template("index.html", memorias=minhas, query=query)

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

        nova_memoria = {
            "id": str(uuid.uuid4()),
            "autor": session['user'],
            "titulo": request.form.get("titulo"),
            "descricao": request.form.get("descricao"),
            "tipo": request.form.get("tipo"),
            "ficheiro": nome_ficheiro
        }

        enviar_socket({"acao": "ADD_CONTEUDO", "dados": nova_memoria})
        return redirect(url_for("index"))

    return render_template("form_post.html")

@app.route("/apagar/<id_memoria>", methods=["GET", "DELETE"])
def apagar(id_memoria):
    if not session.get("user"): return redirect(url_for("login"))

    conteudos = enviar_socket({"acao": "GET_CONTEUDOS"}) or []
    for m in conteudos:
        if m['id'] == id_memoria and m.get('ficheiro'):
            try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], m['ficheiro']))
            except: pass

    enviar_socket({"acao": "DELETE_CONTEUDO", "id": id_memoria})

    if request.method == 'DELETE':
        return {"sucesso": True}

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)