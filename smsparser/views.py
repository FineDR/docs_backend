import requests
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os

class ParseSMSView(APIView):
    def post(self, request):
        sms_text = request.data.get("message")

        if not sms_text:
            return Response({"error": "Missing 'message'"}, status=status.HTTP_400_BAD_REQUEST)

        prompt = f"""
You are an expert SMS transaction parser who understands both English and Kiswahili.

Extract the following fields from the SMS message below and respond ONLY with a valid JSON object:

- type: "Send" or "Receive" (or Kiswahili equivalents: "Tuma" for Send, "Pokea" for Receive)
- amount: transaction amount with currency (e.g., "1,000.00 Tsh")
- sender_name: name of sender or "-"
- sender_number: phone number of sender or "-"
- receiver_name: name of receiver or "-"
- receiver_number: phone number of receiver or "-"
- balance: remaining balance after transaction or "-"
- reference: transaction reference or ID or "-"
- vendor: one of ["Airtel", "Vodacom", "Tigo", "Halotel"] if identifiable from SMS, else "-"

If any information is missing, respond with "-".

SMS:
\"\"\"{sms_text}\"\"\"
"""

        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "DjangoSMSParser"
        }

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            reply = response.json()["choices"][0]["message"]["content"]

            # Extract JSON from the reply safely
            start = reply.find("{")
            end = reply.rfind("}") + 1
            json_part = reply[start:end]

            parsed_json = json.loads(json_part)

            # Extract fields with default fallback "-"
            tx_type = parsed_json.get("type", "-").lower()
            amount = parsed_json.get("amount", "-")
            sender_name = parsed_json.get("sender_name", "-")
            sender_number = parsed_json.get("sender_number", "-")
            receiver_name = parsed_json.get("receiver_name", "-")
            receiver_number = parsed_json.get("receiver_number", "-")
            balance = parsed_json.get("balance", "-")
            reference = parsed_json.get("reference", "-")
            vendor = parsed_json.get("vendor", "-")

            # Adjust sender/receiver based on transaction type
            if tx_type in ["receive", "pokea"]:
                receiver_name = "You"
                receiver_number = "You"
                # sender_name/number remain as parsed or "-"
            elif tx_type in ["send", "tuma"]:
                sender_name = "You"
                sender_number = "You"
                # receiver_name/number remain as parsed or "-"

            # Build clean response dict
            clean_response = {
                "type": tx_type,
                "amount": amount,
                "sender_name": sender_name,
                "sender_number": sender_number,
                "receiver_name": receiver_name,
                "receiver_number": receiver_number,
                "balance": balance,
                "reference": reference,
                "vendor": vendor,
            }

            return Response(clean_response)

        except json.JSONDecodeError:
            return Response({
                "error": "Failed to parse JSON from model response.",
                "raw_response": reply
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
