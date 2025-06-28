from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import httpx
import os

app = FastAPI()

VERIFY_TOKEN = os.getenv("SECRET")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == VERIFY_TOKEN:
        return PlainTextResponse(params.get("hub.challenge"))
    return PlainTextResponse("Invalid verification token", status_code=403)

@app.post("/webhook")
async def receive_webhook(req: Request):
    body = await req.json()
    print("Incoming webhook:", body)

    try:
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        message = value.get("messages", [])[0]
        from_number = message["from"]
        user_text = message["text"]["body"]

        # Respond with a static message (or later with GPT response)
        await send_message(from_number, f"You said: {user_text}")

    except Exception as e:
        print("Error:", e)

    return {"status": "ok"}

async def send_message(to, message):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        print("Sent message:", response.json())

