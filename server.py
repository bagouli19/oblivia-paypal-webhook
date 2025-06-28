from flask import Flask, request, jsonify
import json
import uuid
from datetime import datetime, timedelta
import os

app = Flask(__name__)

CLE_JSON_PATH = "cles_acces.json"

@app.route("/")
def index():
    return "✅ Serveur Flask opérationnel !"

@app.route("/paypal-webhook", methods=["POST"])
def paypal_webhook():
    data = request.json

    event_type = data.get("event_type")
    resource = data.get("resource", {})

    if event_type == "CHECKOUT.ORDER.APPROVED":
        payer_email = resource.get("payer", {}).get("email_address", "unknown")
        amount = float(resource.get("purchase_units", [{}])[0].get("amount", {}).get("value", 0))

        if amount == 3:
            duree = timedelta(days=30)
        elif amount == 20:
            duree = timedelta(days=365)
        elif amount == 50:
            duree = None  # Accès à vie
        else:
            return jsonify({"status": "ignored", "reason": "invalid amount"}), 200

        nouvelle_cle = str(uuid.uuid4())[:8].upper()
        expiration = "illimite" if duree is None else (datetime.now() + duree).strftime("%Y-%m-%d")

        # Charger ou créer le fichier de clés
        if os.path.exists(CLE_JSON_PATH):
            with open(CLE_JSON_PATH, "r") as f:
                cles_data = json.load(f)
        else:
            cles_data = {"cles": [], "admin_key": "ADMIN-ULTIMATE-KEY"}

        cles_data["cles"].append({"cle": nouvelle_cle, "expiration": expiration})

        with open(CLE_JSON_PATH, "w") as f:
            json.dump(cles_data, f, indent=4)

        print(f"✅ Clé générée pour {payer_email} : {nouvelle_cle}")
        return jsonify({"status": "success", "cle": nouvelle_cle}), 200

    return jsonify({"status": "ignored"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)