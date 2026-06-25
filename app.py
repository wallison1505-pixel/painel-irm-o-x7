from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "imperio_scarface_2026"


# =========================
# BANCO DE DADOS
# =========================
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            senha TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            expressao TEXT,
            resultado REAL
        )
    """)

    conn.commit()
    conn.close()

init_db()


# =========================
# LOGIN / CADASTRO
# =========================
@app.route("/")
def home():
    return render_template("login.html")


@app.route("/register", methods=["POST"])
def register():
    usuario = request.form["usuario"]
    senha = request.form["senha"]

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users (usuario, senha) VALUES (?,?)", (usuario, senha))
        conn.commit()
    except:
        pass

    conn.close()
    return redirect("/")


@app.route("/logar", methods=["POST"])
def logar():
    usuario = request.form["usuario"]
    senha = request.form["senha"]

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE usuario=? AND senha=?", (usuario, senha))
    user = c.fetchone()

    conn.close()

    if user:
        session["usuario"] = usuario
        return redirect("/painel")

    return redirect("/")


# =========================
# PAINEL
# =========================
@app.route("/painel")
def painel():
    if "usuario" not in session:
        return redirect("/")

    return render_template("dashboard.html", usuario=session["usuario"])


# =========================
# CALCULO FINANCEIRO
# =========================
@app.route("/calcular", methods=["POST"])
def calcular():
    if "usuario" not in session:
        return jsonify({"ok": False, "erro": "não logado"})

    expr = request.json.get("expressao")

    try:
        resultado = eval(expr)

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        c.execute(
            "INSERT INTO historico (usuario, expressao, resultado) VALUES (?,?,?)",
            (session["usuario"], expr, resultado)
        )

        conn.commit()
        conn.close()

        return jsonify({"ok": True, "resultado": resultado})

    except:
        return jsonify({"ok": False, "erro": "expressão inválida"})


# =========================
# HISTÓRICO
# =========================
@app.route("/historico")
def historico():
    if "usuario" not in session:
        return jsonify([])

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute(
        "SELECT expressao, resultado FROM historico WHERE usuario=? ORDER BY id DESC",
        (session["usuario"],)
    )

    dados = c.fetchall()
    conn.close()

    return jsonify(dados)


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =========================
# START SERVER
# =========================
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)