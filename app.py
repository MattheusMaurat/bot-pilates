
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

ZAPI_INSTANCE_URL = os.getenv('ZAPI_INSTANCE_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def gerar_resposta(mensagem_usuario):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Você é uma especialista em Pilates para mulheres com foco em emagrecimento. Fala de forma acolhedora, motivadora e segura. Sempre tenta ajudar de forma prática."},
            {"role": "user", "content": mensagem_usuario}
        ]
    }
    resposta = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    return resposta.json()['choices'][0]['message']['content']

def enviar_resposta(numero, texto):
    payload = {
        "phone": numero,
        "message": texto
    }
    requests.post(f"{ZAPI_INSTANCE_URL}/send-message", json=payload)

@app.route('/webhook', methods=['POST'])
def webhook():
    dados = request.get_json()
    print("DADOS RECEBIDOS:", dados)  # 👈 Adiciona esse print
    mensagem = dados.get('message', {}).get('body', '')
    numero = dados.get('message', {}).get('phone', '')

    print("Mensagem:", mensagem)       # 👈 Adiciona esse print
    print("Número:", numero)           # 👈 Adiciona esse print

    if mensagem and numero:
        resposta = gerar_resposta(mensagem)
        print("Resposta gerada:", resposta)  # 👈 Adiciona esse print
        enviar_resposta(numero, resposta)

    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
