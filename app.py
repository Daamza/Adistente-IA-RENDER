import os
import openai
from flask import Flask, request, jsonify

openai.api_key = os.getenv("OPENAI_API_KEY")
GPT_MODEL = "gpt-4"

app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    req = request.get_json()
    texto_usuario = req["queryResult"].get("queryText", "")
    print("Consulta recibida:", texto_usuario)
    try:
        respuesta = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "Sos un asistente virtual de laboratorio. Respondé en español y de forma clara."},
                {"role": "user", "content": texto_usuario}
            ]
        ).choices[0].message.content.strip()
        return jsonify({"fulfillmentText": respuesta})
    except Exception as e:
        print("Error GPT:", e)
        return jsonify({"fulfillmentText": "Tuvimos un inconveniente técnico con el asistente. Podés volver a intentar en unos minutos."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))