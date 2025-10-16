import os
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Transaction

# ---------------- Configuration ----------------
BASE_URL = os.getenv("AZAMPAY_BASE_URL", "https://sandbox.azampay.co.tz")
AUTH_BASE_URL = os.getenv("AZAMPAY_AUTH_BASE_URL", "https://authenticator-sandbox.azampay.co.tz")
CLIENT_ID = os.getenv("AZAMPAY_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZAMPAY_CLIENT_SECRET")
CALLBACK_URL = os.getenv("CALLBACK_URL", "http://127.0.0.1:8000/api/payments/azampay/callback/")

# ---------------- Helper Functions ----------------
def get_sandbox_token():
    url = f"{AUTH_BASE_URL}/AppRegistration/GenerateToken"
    payload = {
        "AppName": "smartDocs",
        "clientId": CLIENT_ID.strip(),
        "clientSecret": CLIENT_SECRET.strip()
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        print("TOKEN REQUEST STATUS:", response.status_code)
        print("TOKEN REQUEST RESPONSE:", response.text)
        response.raise_for_status()
        data = response.json()
        token = data.get("data", {}).get("accessToken")
        print("PARSED TOKEN:", token)
        return token
    except Exception as e:
        print("ERROR GETTING TOKEN:", str(e))
        return None

def send_checkout_request(account_number, amount, external_id, provider, token):
    url = f"{BASE_URL}/azampay/mobile/checkout"
    payload = {
        "accountNumber": account_number,
        "amount": amount,
        "currency": "TZS",
        "externalId": external_id,
        "provider": provider,
        "callbackUrl": CALLBACK_URL
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        print("CHECKOUT REQUEST PAYLOAD:", payload)
        print("CHECKOUT RESPONSE STATUS:", response.status_code)
        print("CHECKOUT RESPONSE BODY:", response.text)
        try:
            return response.json(), response.status_code
        except Exception:
            return {"raw_response": response.text}, response.status_code
    except Exception as e:
        print("ERROR DURING CHECKOUT:", str(e))
        return {"error": str(e)}, 500

# ---------------- Views ----------------
@csrf_exempt
def create_checkout(request):
    if request.method != "POST":
        return JsonResponse({"status": "Error", "message": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"status": "Error", "message": "Invalid JSON"}, status=400)

    required_fields = ["accountNumber", "amount", "externalId", "provider"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return JsonResponse({"status": "Error", "message": f"Missing fields: {', '.join(missing)}"}, status=400)

    token = get_sandbox_token()
    if not token:
        return JsonResponse({"status": "Error", "message": "Failed to get sandbox token"}, status=500)

    response_data, status_code = send_checkout_request(
        account_number=data["accountNumber"],
        amount=data["amount"],
        external_id=data["externalId"],
        provider=data["provider"],
        token=token
    )

    return JsonResponse(response_data, status=status_code)

@csrf_exempt
def azampay_callback(request):
    if request.method != "POST":
        return JsonResponse({"status": "Error", "message": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        print("CALLBACK RECEIVED:", data)
    except Exception:
        return JsonResponse({"status": "Error", "message": "Invalid JSON"}, status=400)

    try:
        tx, created = Transaction.objects.update_or_create(
            external_id=data.get("externalId"),
            defaults={
                "status": data.get("status"),
                "amount": data.get("amount"),
                "provider": data.get("provider", ""),
                "account_number": data.get("accountNumber", "")
            }
        )
        print("Transaction saved:", tx.id, "created=", created)
        return JsonResponse({"status": "received"})
    except Exception as e:
        print("ERROR SAVING CALLBACK:", str(e))
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)

