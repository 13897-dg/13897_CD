import os
import json
import uuid
import time
import requests # <-- O GRANDE REGRESSO DO HTTP!
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

# O Endereço da nossa nova API REST
API_URL = "http://api_rest:8000/api"

# --- SISTEMA DE TRADUÇÕES (Mantém-se igual) ---
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

Session(app)

# --- O NOVO HANDSHAKE COM A API REST ---
def aguardar_api():
    print(f"[*] A iniciar o Handshake HTTP com a API REST...")
    tentativas = 10
    for i in range(tentativas):
        try:
            # Tenta fazer um pedido GET simples para ver se a API atende
            requests.get(f"{API_URL}/conteudos", timeout=2)
            print("[+] Sucesso! A API REST acordou e a Base de Dados está pronta.")
            return True
        except requests.exceptions.RequestException:
            print(f"[-] Tentativa {i+1}/{tentativas} falhou. A aguardar a API...")
            time.sleep(3)
    return False

# --- ROTAS DA APLICAÇÃO WEB ---

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            # Fazemos um pedido POST à API para autenticar
            resposta = requests.post(f"{API_URL}/auth", json={"email": email, "password": password}, timeout=3)

            if resposta.status_code == 200:
                session['user'] = email
                if "lang" not in session: session["lang"] = "pt"
                return redirect(url_for('index'))
            else:
                return render_template("formLoginT.html", erro="msg_dados_invalidos")

        except requests.exceptions.RequestException:
            # Se o pedido rebentar (API ou Base de Dados em baixo)
            return render_template("formLoginT.html", erro="msg_db_offline")

    return render_template("formLoginT.html")

@app.route("/registo", methods=["GET", "POST"])
def registo():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            requests.post(f"{API_URL}/users", json={"email": email, "password": password})
            return redirect(url_for("login"))
        except:
            return render_template("formRegistro.html", erro="Erro de ligação.")

    return render_template("formRegistro.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    if not session.get("user"): return redirect(url_for("login"))

    try:
        # Pede TODAS as memórias à API REST
        resposta = requests.get(f"{API_URL}/conteudos")
        todas = resposta.json() if resposta.status_code == 200 else []
    except:
        todas = []

    # Filtra as memórias do utilizador atual
    minhas = [m for m in todas if m['autor'] == session['user']]

    query = request.args.get('q')
    if query:
        query = query.lower()
        minhas = [m for m in minhas if query in m['titulo'].lower() or query in m['descricao'].lower()]

    return render_template("index.html", memorias=minhas, query=query)

@app.route("/dashboard")
def dashboard():
    # Segurança normal: só entra quem tem login feito
    if not session.get("user"): return redirect(url_for("login"))

    dados_tomada = {}

    try:
        url_tomada = "https://cjsg.ddns.net:8443/socket/values"

        resposta = requests.get(url_tomada, timeout=5, verify=False)

        if resposta.status_code == 200:
            dados_tomada = resposta.json()

    except Exception as e:
        print(f"Erro ao espiar a Tomada do Professor: {e}")

    # Enviamos os dados da tomada para a nossa nova página
    return render_template("dashboard.html", socket=dados_tomada)

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

        # O dicionário que vamos enviar para a API guardar no PostgreSQL
        nova_memoria = {
            "id": str(uuid.uuid4()),
            "autor": session['user'],
            "titulo": request.form.get("titulo"),
            "descricao": request.form.get("descricao"),
            "tipo": request.form.get("tipo"),
            "ficheiro": nome_ficheiro,
            "lat": request.form.get("latitude"),
            "lon": request.form.get("longitude")
        }

        try:
            requests.post(f"{API_URL}/conteudos", json=nova_memoria)
        except Exception as e:
            print(f"Erro ao guardar na API: {e}")

        return redirect(url_for("index"))

    return render_template("form_post.html")

@app.route("/apagar/<id_memoria>", methods=["GET", "DELETE"])
def apagar(id_memoria):
    if not session.get("user"):
        if request.method == 'DELETE': return {"erro": "Não autorizado"}, 401
        return redirect(url_for("login"))

    # 1. Obter a memória antes de a apagar (para saber o nome do ficheiro e apagá-lo fisicamente)
    try:
        memorias = requests.get(f"{API_URL}/conteudos").json()
        for m in memorias:
            if m['id'] == id_memoria and m.get('ficheiro'):
                try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], m['ficheiro']))
                except: pass

        # 2. Mandar a API apagar o registo da Base de Dados
        requests.delete(f"{API_URL}/conteudos/{id_memoria}")
    except Exception as e:
        print(f"Erro ao apagar na API: {e}")

    if request.method == 'DELETE':
        return {"sucesso": True}

    return redirect(url_for("index"))

if __name__ == "__main__":
    aguardar_api()
    app.run(host="0.0.0.0", port=5000, debug=True)