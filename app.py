from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Carrega variáveis de ambiente
EVOLUTION_TOKEN = os.getenv("EVOLUTION_TOKEN")
EVOLUTION_INSTANCE_URL = os.getenv("EVOLUTION_INSTANCE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("🔐 EVOLUTION_TOKEN carregado:", EVOLUTION_TOKEN)
print("🌐 EVOLUTION_INSTANCE_URL carregada:", EVOLUTION_INSTANCE_URL)

# Função que gera resposta com ChatGPT
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
        return resposta.json()['choices'][0]['message']['content']
    except KeyError:
        return "Desculpe, algo deu errado ao tentar responder. Tente novamente mais tarde."

# Função para enviar resposta via Evolution

def enviar_resposta(numero, texto):
    url = f"{EVOLUTION_INSTANCE_URL}/message/send-text"

    payload = {
        "number": numero,
        "options": {
            "delay": 1200,
            "presence": "composing"
        },
        "textMessage": {
            "text": texto
        }
    }

    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_TOKEN
    }

    resposta = requests.post(url, json=payload, headers=headers)
    print("📤 RESPOSTA DA EVOLUTION:", resposta.text)

# Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    dados = request.get_json()

    # Ignora grupos
    if dados.get('isGroup'):
        print("❌ Mensagem ignorada: veio de grupo.")
        return jsonify({"status": "ignored"})

    mensagem = dados.get('body', '')
    numero = dados.get('from', '')

    print("🔸 Mensagem recebida:", mensagem)
    print("🔸 Número recebido:", numero)

    if mensagem and numero:
        resposta = gerar_resposta(mensagem)
        print("✅ Resposta gerada:", resposta)
        enviar_resposta(numero, resposta)

    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
