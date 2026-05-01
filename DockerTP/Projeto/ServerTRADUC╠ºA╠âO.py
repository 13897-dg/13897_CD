import os
import json
import uuid
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session

app = Flask(__name__)

# --- CONFIGURAÇÕES ---
app.config["SECRET_KEY"] = "chave_projeto_viagens_2025"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["UPLOAD_FOLDER"] = os.path.join('static', 'uploads')
# Limite de 500MB para permitir vídeos grandes
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024 

# Garante que a pasta de uploads existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- TRATAMENTO DE TRADUÇÕES ---
with open("private/traducoes.json", encoding="utf-8") as f:
    translate = json.load(f) # Carrega as traduções do ficheiro JSON
# Função de tradução
def traducoes(key):
    lang = session.get("lang", "pt")
    return translate.get(lang, translate["pt"]).get(key, key)
# Disponibiliza globalmente a função de tradução nos templates
@app.context_processor
def injetar_tradutor():
    return dict(traducoes=traducoes)
# Rota para mudar idioma
@app.route("/lang/<lang>")
def change_language(lang):
    if lang in translate:
        session["lang"] = lang
    return redirect(request.referrer or url_for("index"))
# Define idioma padrão
@app.before_request
def set_default_language():
    if "lang" not in session:
        session["lang"] = "pt"


# --- SETUP DA BASE DE DADOS (JSON) ---
def inicializar_sistema():
    if not os.path.exists("private"):
        os.makedirs("private")

    # Cria users.json se não existir (Login: viajante@teste.com / 123)
    if not os.path.exists("private/users.json"):
        users_iniciais = [{"email": "viajante@teste.com", "password": "123"}]
        with open("private/users.json", "w", encoding="utf-8") as f:
            json.dump(users_iniciais, f, indent=4)
            
    # Cria conteudos.json se não existir
    if not os.path.exists("private/conteudos.json"):
        with open("private/conteudos.json", "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)

inicializar_sistema()
Session(app)

# --- FUNÇÕES AUXILIARES ---
def load_data(filename):
    try:
        with open(os.path.join("private", filename), "r", encoding="utf-8") as f:
            return json.load(f)
    except: return []

def save_data(filename, data):
    with open(os.path.join("private", filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- ROTAS ---

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        users = load_data("users.json")
        
        for user in users:
            if user['email'] == email and user['password'] == password:
                session['user'] = email
                return redirect(url_for('index'))
        return "Login falhou. <a href='/login'>Tentar de novo</a>"
    return render_template("formLoginT.html")

@app.route("/registo", methods=["GET", "POST"])
def registo():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        users = load_data("users.json")
        
        for user in users:
            if user['email'] == email: return "Email já existe."

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
    minhas = [m for m in todas if m['autor'] == session['user']]
    return render_template("index.html", memorias=minhas)

@app.route("/adicionar", methods=["GET", "POST"])
def adicionar():
    if not session.get("user"): return redirect(url_for("login"))

    if request.method == "POST":
        titulo = request.form.get("titulo")
        descricao = request.form.get("descricao")
        tipo = request.form.get("tipo")
        lat = request.form.get("latitude")
        lon = request.form.get("longitude")
        
        arquivo = request.files.get('ficheiro')
        nome_ficheiro = ""
        
        if arquivo and arquivo.filename != "":
            # Extrai a extensão real do ficheiro (.jpg, .mp4, etc)
            _, extensao = os.path.splitext(arquivo.filename)
            extensao = extensao.lower()
            
            # Se não tiver extensão, forçamos uma baseada no tipo
            if not extensao:
                extensao = '.mp4' if tipo == 'video' else '.jpg'
                
            nome_ficheiro = str(uuid.uuid4()) + extensao
            arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_ficheiro))
        
        nova = {
            "id": str(uuid.uuid4()),
            "autor": session['user'],
            "titulo": titulo,
            "descricao": descricao,
            "tipo": tipo,
            "ficheiro": nome_ficheiro,
            "lat": lat,
            "lon": lon
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
    # Encontrar a memória (next retorna o objeto ou None)
    memoria = next((m for m in dados if m['id'] == id_memoria), None)
    
    # Se não existe ou não pertence ao user, volta ao inicio
    if not memoria or memoria['autor'] != session['user']: 
        return redirect(url_for("index"))

    if request.method == "POST":
        memoria['titulo'] = request.form.get("titulo")
        memoria['descricao'] = request.form.get("descricao")
        memoria['tipo'] = request.form.get("tipo")
        memoria['lat'] = request.form.get("latitude")
        memoria['lon'] = request.form.get("longitude")
        
        arquivo = request.files.get('ficheiro')
        if arquivo and arquivo.filename != "":
            # Apagar antigo (opcional, boa prática)
            if memoria['ficheiro']:
                try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], memoria['ficheiro']))
                except: pass

            # Salvar novo
            _, extensao = os.path.splitext(arquivo.filename)
            extensao = extensao.lower()
            if not extensao: extensao = '.mp4' if memoria['tipo'] == 'video' else '.jpg'
            
            nome_ficheiro = str(uuid.uuid4()) + extensao
            arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_ficheiro))
            memoria['ficheiro'] = nome_ficheiro
        
        save_data("conteudos.json", dados)
        return redirect(url_for("index"))

    # GET: Mostra o formulário preenchido
    return render_template("form_post.html", memoria=memoria)

@app.route("/apagar/<id_memoria>")
def apagar(id_memoria):
    if not session.get("user"): return redirect(url_for("login"))
    
    dados = load_data("conteudos.json")
    # Filtra mantendo apenas as memórias que NÃO têm este ID
    novos = [m for m in dados if m['id'] != id_memoria]
    save_data("conteudos.json", novos)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, port=5001)