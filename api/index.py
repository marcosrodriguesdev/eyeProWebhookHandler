import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime

app = FastAPI()

# Servir arquivos estáticos (como o som)
app.mount("/static", StaticFiles(directory="api/static"), name="static")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

templates = Jinja2Templates(directory="api/templates")


@app.post("/")
async def receber_dados(request: Request):
    data = await request.json()

    async with httpx.AsyncClient() as client:
        # Cria a transação
        response = await client.post(f"{SUPABASE_URL}/rest/v1/transactions", headers=headers, json={
            "local_id": int(data["local_id"]),
            "status": True,  # Em preparo
            "time": data["time"]
        })

        if response.status_code != 201:
            return {"error": "Erro ao criar transação", "details": response.text}

        transaction_id = response.json().get("id")

        # Cria os itens da transação
        for item in data["transaction_items"]:
            await client.post(f"{SUPABASE_URL}/rest/v1/transaction_items", headers=headers, json={
                "transaction_id": transaction_id,
                "product_name": item["product_name"],
                "price": item["price"],
                "quantity": item["quantity"],
                "total": item["total"]
            })

    return {"status": "ok"}


@app.patch("/update_status/{transaction_id}")
async def atualizar_status(transaction_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{SUPABASE_URL}/rest/v1/transactions?id=eq.{transaction_id}",
            headers=headers,
            json={"status": False}  # Pronto
        )
    return {"status": "updated"}


@app.get("/dados", response_class=HTMLResponse)
async def exibir_dados(request: Request):
    today = datetime.now().strftime("%Y-%m-%d")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/transactions"
            f"?select=*,transaction_items(*)"
            f"&time=gte.{today}T00:00:00&time=lt.{today}T23:59:59",
            headers=headers
        )
        transactions = response.json()

    return templates.TemplateResponse("dados.html", {"request": request, "transactions": transactions})
