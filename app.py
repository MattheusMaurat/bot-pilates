
from flask import Flask, request, jsonify
import requests
import os
import os

ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")
print("🔍 TOKEN CARREGADO:", ZAPI_CLIENT_TOKEN)

app = Flask(__name__)

ZAPI_INSTANCE_URL = os.getenv('ZAPI_INSTANCE_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

print("🔍 ZAPI_INSTANCE_URL carregada:", ZAPI_INSTANCE_URL)

def gerar_resposta(mensagem_usuario):
    headers = {
        "Authorization": f"Bearer " + OPENAI_API_KEY,
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
    
    print("🧠 RESPOSTA DA OPENAI:", resposta.text)  # 👈 Adiciona isso

    try:
        return resposta.json()['choices'][0]['message']['content']
    except KeyError:
        return "Desculpe, algo deu errado ao tentar responder. Tente novamente mais tarde."


def enviar_resposta(numero, texto):
    url = f"https://api.z-api.io/instances/{os.getenv('ZAPI_INSTANCE_ID')}/send-text"

    payload = {
        "phone": numero,
        "message": texto
    }

    headers = {
        "Content-Type": "application/json",
        "Client-Token": os.getenv("ZAPI_CLIENT_TOKEN")
    }

    print("📤 URL final:", url)
    print("📤 Payload:", payload)
    print("📤 Headers:", headers)

    resposta = requests.post(url, json=payload, headers=headers)
    print("📥 RESPOSTA DA ZAPI:", resposta.text)


@app.route('/webhook', methods=['POST'])
def webhook():
    dados = request.get_json()

     # Ignora grupos
    if dados.get('isGroup'):
        print("❌ Mensagem ignorada: veio de grupo.")
        return jsonify({"status": "ignored"})

    mensagem = dados.get('text', {}).get('message', '')
    numero = dados.get('phone', '')

    print("🔸 Mensagem recebida:", mensagem)
    print("🔸 Número recebido:", numero)

    if mensagem and numero:
        resposta = gerar_resposta(mensagem)
        print("✅ Resposta gerada:", resposta)
        enviar_resposta(numero, resposta)

    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


