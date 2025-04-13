
from flask import Flask, request, jsonify
import base64
import io
from PIL import Image
import pytesseract
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    req = request.get_json()
    intent = req["queryResult"]["intent"]["displayName"]
    parameters = req["queryResult"].get("parameters", {})

    if intent == "Saludo":
        return jsonify({"fulfillmentText": "Hola, ¿podés enviarme tu orden médica o consultarme por un turno?"})

    elif intent == "PedirTurno":
        nombre = parameters.get("nombre", "Paciente")
        fecha = datetime.datetime.now().strftime("%Y-%m-%d")
        hora = datetime.datetime.now().strftime("%H:%M")

        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("Turnos_Laboratorio").sheet1
        sheet.append_row([nombre, fecha, hora])

        return jsonify({"fulfillmentText": f"Turno asignado para {nombre}, el {fecha} a las {hora}."})

    elif intent == "EnviarImagenOrden":
        imagen_b64 = parameters.get("imagen_b64", "")
        if imagen_b64:
            try:
                image_data = base64.b64decode(imagen_b64)
                image = Image.open(io.BytesIO(image_data))
                texto = pytesseract.image_to_string(image)
                if texto.strip():
                    return jsonify({"fulfillmentText": f"Texto leído de la orden médica: {texto}"})
                else:
                    return jsonify({"fulfillmentText": "No pude leer el contenido de la imagen. ¿Podés reenviarla?"})
            except Exception as e:
                return jsonify({"fulfillmentText": f"Error al procesar la imagen: {str(e)}"})
        else:
            return jsonify({"fulfillmentText": "No se recibió imagen para analizar."})

    else:
        return jsonify({"fulfillmentText": "No comprendí tu mensaje. ¿Podés repetirlo o enviar tu orden médica?"})

if __name__ == "__main__":
    app.run()
