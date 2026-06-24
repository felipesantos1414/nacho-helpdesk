import os
import json
import sqlite3
import uuid
import re
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session

# ─── App Setup ───────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "nacho-helpdesk-cs50x-2025")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "helpdesk.db")

# ─── DB Helpers ──────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    from database.init_db import init_database
    init_database()


# ─── Keyword Matcher ─────────────────────────────────────────────────────────
def find_best_problem(user_message: str):
    """Score each problem by keyword matches and return the best one."""
    msg = user_message.lower()
    conn = get_db()
    problems = conn.execute("SELECT * FROM problems").fetchall()
    conn.close()

    best_score = 0
    best_problem = None

    for p in problems:
        keywords = [k.strip() for k in p["keywords"].split(",")]
        score = sum(1 for kw in keywords if kw in msg)
        # Also partial title match
        title_words = p["title"].lower().split()
        score += sum(1 for w in title_words if len(w) > 3 and w in msg)
        if score > best_score:
            best_score = score
            best_problem = p

    return best_problem if best_score >= 1 else None


# ─── AI Enhancement via Anthropic ────────────────────────────────────────────
import urllib.request

def ask_claude(user_message: str, solution: str, problem_title: str) -> str:
    """Call Anthropic API to enrich the helpdesk solution response."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        # Fallback: return the DB solution formatted nicely
        return None

    system_prompt = (
        "Você é Nacho, um assistente de HelpDesk de TI simpático e eficiente. "
        "Sua personalidade é amigável como um cachorro Beagle fiel. "
        "Responda SOMENTE sobre problemas de TI/HelpDesk. "
        "Use a solução fornecida como base, mas personalize para a mensagem do usuário. "
        "Seja conciso, use listas numeradas, e termine perguntando se ajudou. "
        "Responda em português do Brasil. Máximo 200 palavras."
    )

    prompt = (
        f"O usuário disse: '{user_message}'\n\n"
        f"Problema identificado: {problem_title}\n\n"
        f"Solução base:\n{solution}\n\n"
        "Adapte a resposta para o usuário de forma amigável."
    )

    payload = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 400,
        "system": system_prompt,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data["content"][0]["text"]
    except Exception:
        return None


# ─── Session Helpers ──────────────────────────────────────────────────────────
def get_or_create_session():
    if "sid" not in session:
        session["sid"] = str(uuid.uuid4())
    sid = session["sid"]
    conn = get_db()
    row = conn.execute("SELECT * FROM sessions WHERE id=?", (sid,)).fetchone()
    if not row:
        conn.execute("INSERT INTO sessions (id) VALUES (?)", (sid,))
        conn.commit()
    conn.close()
    return sid


def get_off_topic_count(sid):
    conn = get_db()
    row = conn.execute("SELECT off_topic_count, closed FROM sessions WHERE id=?", (sid,)).fetchone()
    conn.close()
    return (row["off_topic_count"], row["closed"]) if row else (0, 0)


def increment_off_topic(sid):
    conn = get_db()
    conn.execute("UPDATE sessions SET off_topic_count = off_topic_count + 1 WHERE id=?", (sid,))
    conn.commit()
    row = conn.execute("SELECT off_topic_count FROM sessions WHERE id=?", (sid,)).fetchone()
    count = row["off_topic_count"] if row else 1
    conn.close()
    return count


def reset_off_topic(sid):
    conn = get_db()
    conn.execute("UPDATE sessions SET off_topic_count = 0 WHERE id=?", (sid,))
    conn.commit()
    conn.close()


def close_session(sid):
    conn = get_db()
    conn.execute("UPDATE sessions SET closed = 1 WHERE id=?", (sid,))
    conn.commit()
    conn.close()


# ─── Routes ──────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    conn = get_db()
    total_problems = conn.execute("SELECT COUNT(*) as c FROM problems").fetchone()["c"]
    total_interactions = conn.execute("SELECT COUNT(*) as c FROM interactions").fetchone()["c"]
    helpful_count = conn.execute("SELECT COUNT(*) as c FROM interactions WHERE was_helpful=1").fetchone()["c"]
    resolution_rate = round((helpful_count / total_interactions * 100) if total_interactions > 0 else 89)
    total_sessions = conn.execute("SELECT COUNT(DISTINCT session_id) as c FROM interactions").fetchone()["c"]

    # Top problems
    top_problems = conn.execute("""
        SELECT p.title, p.category, COUNT(i.id) as count
        FROM problems p
        LEFT JOIN interactions i ON i.problem_id = p.id
        GROUP BY p.id ORDER BY count DESC LIMIT 5
    """).fetchall()

    # Recent activity
    recent = conn.execute("""
        SELECT user_message, timestamp
        FROM interactions
        ORDER BY timestamp DESC LIMIT 6
    """).fetchall()

    # Interactions by day (last 7)
    interactions_today = conn.execute("""
        SELECT COUNT(*) as c FROM interactions
        WHERE date(timestamp) = date('now')
    """).fetchone()["c"]

    conn.close()
    return render_template("dashboard.html",
        total_problems=total_problems,
        total_interactions=total_interactions,
        resolution_rate=resolution_rate,
        total_sessions=total_sessions,
        top_problems=top_problems,
        recent=recent,
        interactions_today=interactions_today
    )


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    lang = data.get("lang", "pt")

    if not user_message:
        return jsonify({"error": "Mensagem vazia"}), 400

    sid = get_or_create_session()
    off_topic_count, closed = get_off_topic_count(sid)

    if closed:
        msg = (
            "This session has ended. Please reload the page to start a new conversation."
            if lang == "en" else
            "Esta sessão foi encerrada. Por favor, recarregue a página para iniciar uma nova conversa."
        )
        return jsonify({"response": msg, "closed": True})

    # Find matching problem
    problem = find_best_problem(user_message)

    if problem:
        reset_off_topic(sid)

        # Pick solution in the right language
        solution_text = problem["solution_en"] if (lang == "en" and problem["solution_en"]) else problem["solution"]

        # Try AI enhancement, fallback to DB solution
        ai_response = ask_claude(user_message, solution_text, problem["title"])
        response_text = ai_response if ai_response else format_solution(solution_text, lang)

        # Log interaction
        conn = get_db()
        conn.execute(
            "INSERT INTO interactions (session_id, user_message, bot_response, problem_id) VALUES (?,?,?,?)",
            (sid, user_message, response_text, problem["id"])
        )
        conn.execute("UPDATE problems SET usage_count = usage_count + 1 WHERE id=?", (problem["id"],))
        conn.commit()
        conn.close()

        return jsonify({
            "response": response_text,
            "problem_id": problem["id"],
            "problem_title": problem["title"],
            "show_feedback": True,
            "closed": False
        })

    else:
        new_count = increment_off_topic(sid)
        remaining = 3 - new_count

        if new_count >= 3:
            close_session(sid)
            response_text = (
                "Woof! 🐾 I tried to help, but I could not identify a HelpDesk problem in your messages. "
                "For security, this session will now close. Reload the page to start again. "
                "Remember: I only handle IT support issues!"
                if lang == "en" else
                "Au au! 🐾 Tentei te ajudar, mas não consegui identificar um problema de HelpDesk "
                "nas suas mensagens. Por segurança, vou encerrar esta sessão. "
                "Recarregue a página para iniciar uma nova conversa. "
                "Lembre-se: sou especialista em problemas de TI!"
            )
            conn = get_db()
            conn.execute(
                "INSERT INTO interactions (session_id, user_message, bot_response) VALUES (?,?,?)",
                (sid, user_message, response_text)
            )
            conn.commit()
            conn.close()
            return jsonify({"response": response_text, "closed": True})

        if lang == "en":
            attempts = f"({remaining} attempt{'s' if remaining > 1 else ''} remaining)"
            friendly_msgs = [
                f"Woof! 🐾 I'm Nacho, your IT specialist! I couldn't identify your HelpDesk problem. Can you describe it better? For example: 'I cannot access the VPN' or 'my printer is not printing'. {attempts}",
                f"Woof! 🐶 Hmm, I still didn't understand your IT issue. Try being more specific! Examples: email, Wi-Fi, password, printer, slow computer... {attempts}",
            ]
        else:
            attempts = f"({remaining} tentativa{'s' if remaining > 1 else ''} restante{'s' if remaining > 1 else ''})"
            friendly_msgs = [
                f"Au! 🐾 Sou o Nacho, especialista em TI! Não consegui identificar seu problema de HelpDesk. Pode descrever melhor? Por exemplo: 'não consigo acessar a VPN' ou 'minha impressora não imprime'. {attempts}",
                f"Woof! 🐶 Hmm, ainda não entendi seu problema de TI. Tente ser mais específico! Exemplos: problemas com e-mail, Wi-Fi, senha, impressora, computador lento... {attempts}",
            ]
        response_text = friendly_msgs[min(new_count - 1, len(friendly_msgs) - 1)]

        conn = get_db()
        conn.execute(
            "INSERT INTO interactions (session_id, user_message, bot_response) VALUES (?,?,?)",
            (sid, user_message, response_text)
        )
        conn.commit()
        conn.close()

        return jsonify({"response": response_text, "closed": False, "show_feedback": False})


@app.route("/api/feedback", methods=["POST"])
def feedback():
    data = request.get_json()
    problem_id = data.get("problem_id")
    helpful = data.get("helpful", False)
    sid = session.get("sid")

    if not sid or not problem_id:
        return jsonify({"ok": False}), 400

    conn = get_db()
    # Update the most recent interaction for this session+problem
    conn.execute("""
        UPDATE interactions SET was_helpful=?
        WHERE session_id=? AND problem_id=?
        ORDER BY timestamp DESC LIMIT 1
    """, (1 if helpful else 0, sid, problem_id))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/new-session", methods=["POST"])
def new_session():
    session.pop("sid", None)
    return jsonify({"ok": True})


@app.route("/api/problems")
def get_problems():
    conn = get_db()
    problems = conn.execute("SELECT id, title, category, keywords FROM problems ORDER BY id").fetchall()
    conn.close()
    return jsonify([dict(p) for p in problems])


@app.route("/api/stats")
def stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) as c FROM interactions").fetchone()["c"]
    helpful = conn.execute("SELECT COUNT(*) as c FROM interactions WHERE was_helpful=1").fetchone()["c"]
    rate = round((helpful / total * 100) if total > 0 else 0)
    
    categories = conn.execute("""
        SELECT p.category, COUNT(i.id) as count
        FROM problems p
        JOIN interactions i ON i.problem_id = p.id
        GROUP BY p.category ORDER BY count DESC
    """).fetchall()
    conn.close()
    return jsonify({
        "total": total,
        "resolution_rate": rate,
        "categories": [dict(r) for r in categories]
    })


def format_solution(solution_text: str, lang: str = "pt") -> str:
    """Format the plain solution text as a friendly response."""
    if lang == "en":
        header = "Woof! Let\'s fix this together! 🐾\n\nHere are the steps to resolve it:\n\n"
        footer = "\n\nDid these tips help?"
    else:
        header = "Au! Vamos resolver isso juntos! 🐾\n\nAqui estão as etapas para resolver:\n\n"
        footer = "\n\nEssas dicas ajudaram?"
    return header + solution_text + footer


# ─── Run ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
