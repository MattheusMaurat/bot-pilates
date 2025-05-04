from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")  # Ex: https://seudominio.com.br
EVOLUTION_INSTANCE_ID = os.getenv("EVOLUTION_INSTANCE_ID")  # ID da instância criada
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")  # API Key da Evolution
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def gerar_resposta(mensagem_usuario):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Você é uma especialista em Pilates para mulheres com foco em emagrecimento."},
            {"role": "user", "content": mensagem_usuario}
        ]
    }

    resposta = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    print("🧠 RESPOSTA DA OPENAI:", resposta.text)

    try:
        return resposta.json()["choices"][0]["message"]["content"]
    except:
        return "Desculpe, houve um erro ao gerar a resposta."

def enviar_resposta(numero, mensagem):
    url = f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE_ID}"
    payload = {
        "number": numero.split("@")[0],
        "options": {
            "delay": 0,
            "presence": "composing"
        },
        "textMessage": {
            "text": mensagem
        }
    }
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }

    print("📤 Enviando para Evolution:", url)
    print("📤 Payload:", payload)
    resposta = requests.post(url, json=payload, headers=headers)
    print("📥 RESPOSTA DA EVOLUTION:", resposta.text)

@app.post("/webhook")
def handle_message(request: Request):
    payload = request.json()
    remote_jid = payload['data']['key']['remoteJid']

    # ✅ FILTRO PARA IGNORAR GRUPOS
    if remote_jid.endswith("@g.us"):
        print("Mensagem de grupo ignorada.")
        return {"status": "ok"}

@app.route('/webhook', methods=['POST'])
def webhook():
    dados = request.get_json()
    print("📥 DADOS RECEBIDOS:", dados)

    # Ignora eventos que não são mensagens
    if dados.get("event") != "messages.upsert":
        print(f"❌ Evento ignorado: {dados.get('event')}")
        return jsonify({"status": "ignored"})

    # Captura a mensagem e número
    mensagem_info = dados.get("data", {})
    mensagem = mensagem_info.get("message", {}).get("conversation", "")
    numero = mensagem_info.get("key", {}).get("remoteJid", "")
    from_me = mensagem_info.get("key", {}).get("fromMe", True)

    # Ignora mensagens enviadas por você mesmo
    if from_me:
        print("❌ Ignorado: mensagem enviada pelo bot.")
        return jsonify({"status": "ignored"})

    print("📩 Mensagem recebida:", mensagem)
    print("📞 Número:", numero)

    if mensagem and numero:
        resposta = gerar_resposta(mensagem)
        print("✅ Resposta gerada:", resposta)
        enviar_resposta(numero, resposta)

    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
