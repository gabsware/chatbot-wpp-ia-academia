from flask import Flask, request, jsonify
import json, os
from google import genai

# ===== CONFIG IA =====
client = genai.Client(api_key="chave-api-gemini")

app = Flask(__name__)
DB_FILE = "db.json"

# ===== DB =====
def load_db():
    if not os.path.exists(DB_FILE):
        return {"usuarios": {}}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

# ===== IA =====
def perguntar_ia(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print("ERRO IA:", e)
        return "Erro na IA"

# ===== ROTAS =====
@app.route("/")
def home():
    return "Bot online"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        user = data.get("from")
        msg = data.get("message", "").strip().lower()

        db = load_db()

        if user not in db["usuarios"]:
            db["usuarios"][user] = {"estado": None}
            save_db(db)

        user_data = db["usuarios"][user]

        MENU = (
            "📋 MENU:\n"
            "1 - Explicar exercício\n"
            "2 - Substituir exercício\n"
            "3 - Alongamento\n"
            "4 - Fortalecimento\n"
            "0 - Cancelar"
        )

        # ===== RESET =====
        if msg == "menu":
            user_data["estado"] = None
            save_db(db)
            return jsonify({"reply": MENU})

        # ===== CANCELAR =====
        if msg == "0":
            user_data["estado"] = None
            save_db(db)
            return jsonify({"reply": "❌ Operação cancelada.\nDigite 'menu'."})

        # ===== TROCA DE OPÇÃO =====
        if msg in ["1", "2", "3", "4"]:
            user_data["estado"] = None

        # ===== 1 - EXPLICAR =====
        if msg == "1":
            user_data["estado"] = "explicar"
            save_db(db)
            return jsonify({"reply": "Qual exercício deseja? (ou 0 para cancelar)"})

        elif user_data["estado"] == "explicar":
            user_data["estado"] = None
            save_db(db)

            resposta = perguntar_ia(
                f"Explique o exercício {msg} como um personal trainer, com execução correta e dicas."
            )

            return jsonify({"reply": resposta})

        # ===== 2 - SUBSTITUIR =====
        if msg == "2":
            user_data["estado"] = "substituir"
            save_db(db)
            return jsonify({"reply": "Qual exercício deseja substituir? (ou 0 para cancelar)"})

        elif user_data["estado"] == "substituir":
            user_data["estado"] = None
            save_db(db)

            resposta = perguntar_ia(
                f"Substitua o exercício {msg} por outro equivalente que trabalhe os mesmos músculos."
            )

            return jsonify({"reply": resposta})

        # ===== 3 - ALONGAMENTO =====
        if msg == "3":
            user_data["estado"] = "alongamento"
            save_db(db)
            return jsonify({"reply": "Qual parte do corpo deseja alongar ou sente dor? (ou 0 para cancelar)"})

        elif user_data["estado"] == "alongamento":
            user_data["estado"] = None
            save_db(db)

            resposta = perguntar_ia(
                f"Sugira alongamentos para a região {msg}, com explicação simples e segura."
            )

            return jsonify({"reply": resposta})

        # ===== 4 - FORTALECIMENTO =====
        if msg == "4":
            user_data["estado"] = "fortalecimento"
            save_db(db)
            return jsonify({"reply": "Qual parte do corpo deseja fortalecer? (ou 0 para cancelar)"})

        elif user_data["estado"] == "fortalecimento":
            user_data["estado"] = None
            save_db(db)

            resposta = perguntar_ia(
                f"Sugira exercícios de fortalecimento para a região {msg}, com instruções simples."
            )

            return jsonify({"reply": resposta})

        # ===== PADRÃO =====
        return jsonify({"reply": "Digite 'menu' para começar."})

    except Exception as e:
        print("ERRO:", e)
        return jsonify({"reply": "Erro no servidor"})

if __name__ == "__main__":
    app.run(port=5000)
