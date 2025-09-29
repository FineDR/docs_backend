import os
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Transaction

# --- AzamPay configuration ---
BASE_URL = os.getenv("AZAMPAY_BASE_URL", "https://sandbox.azampay.co.tz")
AUTH_BASE_URL = "https://authenticator-sandbox.azampay.co.tz"
CLIENT_ID = os.getenv("AZAMPAY_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZAMPAY_CLIENT_SECRET")


def get_sandbox_token():
    """
    Generate sandbox access token from AzamPay Authenticator sandbox
    """
    url = f"{AUTH_BASE_URL}/oauth/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET.strip()  # Remove any extra spaces/line breaks
    }

    try:
        res = requests.post(url, json=payload, timeout=15)
        print("Token response status:", res.status_code)
        print("Token response body:", res.text)

        if res.status_code != 200:
            # Log the failure and return None
            print("Failed to fetch token. Check client_id / client_secret / sandbox app.")
            return None

        data = res.json()
        token = data.get("access_token")
        if not token:
            print("Access token not found in response:", data)
            return None

        return token

    except requests.RequestException as e:
        print("HTTP Request error while fetching token:", str(e))
        return None
    except Exception as e:
        print("Unexpected error while fetching token:", str(e))
        return None


@csrf_exempt
def create_checkout(request):
    if request.method != "POST":
        return JsonResponse({"status": "Error", "message": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "Error", "message": "Invalid JSON"}, status=400)

    required_fields = ["accountNumber", "amount", "externalId", "provider"]
    missing_fields = [f for f in required_fields if not data.get(f)]
    if missing_fields:
        return JsonResponse({"status": "Error", "message": f"Missing fields: {', '.join(missing_fields)}"}, status=400)

    # Get sandbox token
    token = get_sandbox_token()
    if not token:
        return JsonResponse({"status": "Error", "message": "Unable to get sandbox token. Check your AzamPay credentials."}, status=500)

    payload = {
        "accountNumber": data["accountNumber"],
        "amount": data["amount"],
        "currency": "TZS",
        "externalId": data["externalId"],
        "provider": data["provider"]
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(f"{BASE_URL}/azampay/mno/checkout", headers=headers, json=payload, timeout=15)
        try:
            return JsonResponse(res.json(), status=res.status_code)
        except json.JSONDecodeError:
            # In case AzamPay returns non-JSON error
            return JsonResponse({"status": "Error", "message": res.text}, status=res.status_code)
    except requests.RequestException as e:
        print("HTTP error during checkout:", str(e))
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)


@csrf_exempt
def azampay_callback(request):
    if request.method != "POST":
        return JsonResponse({"status": "Error", "message": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
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
        print("Callback received:", data)
        return JsonResponse({"status": "received"})
    except Exception as e:
        print("Error saving callback:", str(e))
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
