import os
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Transaction

# ---------------------------------------------------
# Azampay Configuration
# ---------------------------------------------------
BASE_URL = os.getenv("AZAMPAY_BASE_URL", "https://sandbox.azampay.co.tz")
AUTH_BASE_URL = os.getenv("AZAMPAY_AUTH_BASE_URL", "https://authenticator-sandbox.azampay.co.tz")
CLIENT_ID = os.getenv("AZAMPAY_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZAMPAY_CLIENT_SECRET")

CALLBACK_URL = os.getenv(
    "CALLBACK_URL",
    "https://precarnival-lourdes-podsolic.ngrok-free.dev/api/v1/Checkout/Callback/"
)

WEBHOOK_URL = os.getenv(
    "WEBHOOK_URL",
    "https://precarnival-lourdes-podsolic.ngrok-free.dev/api/payments/webhook/"
)

# ---------------------------------------------------
# Helper: Get Sandbox Token
# ---------------------------------------------------
def get_sandbox_token():
    url = f"{AUTH_BASE_URL}/AppRegistration/GenerateToken"
    payload = {
        "AppName": "smartDocs",
        "clientId": CLIENT_ID.strip(),
        "clientSecret": CLIENT_SECRET.strip(),
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print("TOKEN RESPONSE:", response.status_code, response.text)
        response.raise_for_status()
        data = response.json()
        token = data.get("data", {}).get("accessToken")
        if not token:
            print("TOKEN ERROR: No access token returned in response.")
        return token
    except requests.exceptions.RequestException as e:
        print("TOKEN REQUEST EXCEPTION:", str(e))
        if hasattr(e, "response") and e.response is not None:
            print("TOKEN RESPONSE CONTENT:", e.response.text)
        return None
    except Exception as e:
        print("TOKEN ERROR:", str(e))
        return None

# ---------------------------------------------------
# Helper: Send Payment Checkout Request
# ---------------------------------------------------
def send_checkout_request(account_number, amount, external_id, provider, token):
    url = f"{BASE_URL}/azampay/mno/checkout"

    payload = {
        "accountNumber": account_number,
        "amount": amount,
        "currency": "TZS",
        "externalId": external_id,
        "provider": provider,
        "additionalProperties": {}
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        print("CHECKOUT RESPONSE STATUS:", response.status_code)
        print("CHECKOUT RESPONSE BODY:", response.text)
        response.raise_for_status()
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        print("CHECKOUT REQUEST EXCEPTION:", str(e))
        if hasattr(e, "response") and e.response is not None:
            print("CHECKOUT RESPONSE CONTENT:", e.response.text)
        return {"error": str(e)}, 500
    except Exception as e:
        print("CHECKOUT ERROR:", str(e))
        return {"error": str(e)}, 500

# ---------------------------------------------------
# 1. INITIATE PAYMENT (Optional)
# ---------------------------------------------------
@csrf_exempt
def initiate_payment(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    return JsonResponse({
        "status": "ok",
        "message": "Payment initiation started."
    })

# ---------------------------------------------------
# 2. CREATE CHECKOUT
# ---------------------------------------------------
@csrf_exempt
def create_checkout(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)

    # Parse JSON payload
    try:
        data = json.loads(request.body)
    except Exception as e:
        print("CREATE CHECKOUT JSON ERROR:", str(e))
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    # Validate required fields
    required = ["accountNumber", "amount", "externalId", "provider"]
    missing = [f for f in required if f not in data]

    if missing:
        return JsonResponse({"status": "error", "message": f"Missing fields: {missing}"}, status=400)

    # Get Azampay token
    token = get_sandbox_token()
    if not token:
        return JsonResponse({"status": "error", "message": "Cannot get Azampay token"}, status=500)

    # Send checkout request to Azampay
    response_data, status_code = send_checkout_request(
        data["accountNumber"],
        data["amount"],
        data["externalId"],
        data["provider"],
        token,
    )

    # Save transaction in database
    try:
        tx, created = Transaction.objects.update_or_create(
            external_id=data["externalId"],
            defaults={
                "account_number": data["accountNumber"],
                "provider": data["provider"],
                "amount": data["amount"],
                "transaction_id": response_data.get("transactionId"),
                "status": "PENDING",
                "raw_checkout": response_data,
            },
        )
        print("TRANSACTION SAVED:", tx.id)
    except Exception as e:
        print("SAVE TRANSACTION ERROR:", e)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

    # Return response
    return JsonResponse({
        "success": response_data.get("success", False),
        "transactionId": tx.transaction_id,
        "message": response_data.get("message", "Transaction processed"),
    }, status=status_code)

# ---------------------------------------------------
# 3. CALLBACK (From Azampay)
# ---------------------------------------------------
@csrf_exempt
def azampay_callback(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        print("CALLBACK RECEIVED:", data)
    except Exception as e:
        print("CALLBACK JSON ERROR:", str(e))
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    try:
        tx, created = Transaction.objects.update_or_create(
            external_id=data.get("externalId"),
            defaults={
                "status": data.get("status"),
                "amount": data.get("amount"),
                "provider": data.get("provider", ""),
                "account_number": data.get("accountNumber", ""),
                "raw_callback": data,
            },
        )
        print("CALLBACK SAVED:", tx.id)
    except Exception as e:
        print("SAVE CALLBACK ERROR:", e)
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"status": "received"})

# ---------------------------------------------------
# 4. WEBHOOK (Final Confirmation)
# ---------------------------------------------------
@csrf_exempt
def webhook_handler(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        print("WEBHOOK RECEIVED:", data)
    except Exception as e:
        print("WEBHOOK JSON ERROR:", str(e))
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    try:
        tx, created = Transaction.objects.update_or_create(
            external_id=data.get("externalId"),
            defaults={
                "status": data.get("status"),
                "amount": data.get("amount"),
                "provider": data.get("channel", ""),
                "raw_webhook": data,
            },
        )
        print("WEBHOOK SAVED:", tx.id)
    except Exception as e:
        print("WEBHOOK SAVE ERROR:", e)
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"status": "success"})
