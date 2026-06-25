from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import os

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

    c.execute("""
        CREATE TABLE IF NOT EXISTS diario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            data TEXT,
            valor REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS banca (
            usuario TEXT PRIMARY KEY,
            inicial REAL
        )
    """)

    conn.commit()
    conn.close()

init_db()


# =========================
# LOGIN
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
# CALCULADORA
# =========================
@app.route("/calcular", methods=["POST"])
def calcular():
    if "usuario" not in session:
        return jsonify({"ok": False})

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
        return jsonify({"ok": False})


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
# 📅 CALENDÁRIO
# =========================
@app.route("/registrar_dia", methods=["POST"])
def registrar_dia():
    if "usuario" not in session:
        return jsonify({"ok": False})

    data = request.json.get("data")
    valor = float(request.json.get("valor"))

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO diario (usuario, data, valor) VALUES (?,?,?)",
        (session["usuario"], data, valor)
    )

    conn.commit()
    conn.close()

    return jsonify({"ok": True})


@app.route("/calendario")
def calendario():
    if "usuario" not in session:
        return jsonify([])

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute(
        "SELECT data, valor FROM diario WHERE usuario=? ORDER BY data DESC",
        (session["usuario"],)
    )

    dados = c.fetchall()
    conn.close()

    return jsonify(dados)


# =========================
# 💰 BANCA
# =========================
@app.route("/set_banca", methods=["POST"])
def set_banca():
    if "usuario" not in session:
        return jsonify({"ok": False})

    valor = float(request.json.get("valor"))

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO banca (usuario, inicial)
        VALUES (?, ?)
        ON CONFLICT(usuario) DO UPDATE SET inicial=excluded.inicial
    """, (session["usuario"], valor))

    conn.commit()
    conn.close()

    return jsonify({"ok": True})


@app.route("/saldo")
def saldo():
    if "usuario" not in session:
        return jsonify({"saldo": 0})

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("SELECT inicial FROM banca WHERE usuario=?", (session["usuario"],))
    banca = c.fetchone()
    inicial = banca[0] if banca else 0

    c.execute("SELECT SUM(valor) FROM diario WHERE usuario=?", (session["usuario"],))
    movimento = c.fetchone()[0]
    movimento = movimento if movimento else 0

    saldo_final = float(inicial) + float(movimento)

    conn.close()

    return jsonify({
        "inicial": inicial,
        "movimento": movimento,
        "saldo": saldo_final
    })


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =========================
# START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)