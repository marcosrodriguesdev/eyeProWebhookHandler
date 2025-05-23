import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

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

    # Envia para a tabela 'transactions'
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{SUPABASE_URL}/rest/v1/transactions", headers=headers, json={
            "local_id": data["local_id"],
            "status": data["status"],
            "time": data["time"]
        })
        transaction_id = response.json().get("id")

        # Envia os itens para 'transaction_items'
        for item in data["transaction_items"]:
            await client.post(f"{SUPABASE_URL}/rest/v1/transaction_items", headers=headers, json={
                "transaction_id": transaction_id,
                "product_name": item["product_name"],
                "price": item["price"],
                "quantity": item["quantity"],
                "total": item["total"]
            })

    return {"status": "ok"}


@app.get("/dados", response_class=HTMLResponse)
async def exibir_dados(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/transactions?select=*,transaction_items(*)",
            headers=headers
        )

        transactions = response.json()

    return templates.TemplateResponse("dados.html", {"request": request, "transactions": transactions})
