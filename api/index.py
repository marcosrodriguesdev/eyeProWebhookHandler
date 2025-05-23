import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
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
    try:
        data = await request.json()
        print("📥 Dados recebidos do webhook:", data)

        async with httpx.AsyncClient() as client:
            # Criar transação
            response = await client.post(
                f"{SUPABASE_URL}/rest/v1/transactions",
                headers=headers,
                json={
                    "local_id": int(data["local_id"]),
                    "status": False,
                    "time": data["time"]
                }
            )
            print("📤 Resposta da criação da transação:", response.status_code, response.text)

            if response.status_code != 201:
                return JSONResponse(
                    content={"error": "Erro ao criar transação", "details": response.text},
                    status_code=500
                )

            transaction_id = response.json().get("id")

            # Criar itens da transação
            for item in data["transaction_items"]:
                item_response = await client.post(
                    f"{SUPABASE_URL}/rest/v1/transaction_items",
                    headers=headers,
                    json={
                        "transaction_id": transaction_id,
                        "product_name": item["product_name"],
                        "price": item["price"],
                        "quantity": item["quantity"],
                        "total": item["total"]
                    }
                )
                print("📤 Resposta da criação do item:", item_response.status_code, item_response.text)

        print("✅ Transação e itens criados com sucesso")
        return JSONResponse(content={"status": "ok"}, status_code=200)

    except Exception as e:
        print("❌ Erro ao processar webhook:", str(e))
        return JSONResponse(content={"error": "Erro interno", "details": str(e)}, status_code=500)


@app.patch("/update_status/{transaction_id}")
async def atualizar_status(transaction_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{SUPABASE_URL}/rest/v1/transactions?id=eq.{transaction_id}",
            headers=headers,
            json={"status": True}
        )
    return {"status": "updated"}


@app.get("/dados", response_class=HTMLResponse)
async def exibir_dados(request: Request):
    today = datetime.now().strftime("%Y-%m-%d")
    async with httpx.AsyncClient() as client:
        response_em_preparo = await client.get(
            f"{SUPABASE_URL}/rest/v1/transactions?select=*,transaction_items(*)"
            f"&time=gte.{today}T00:00:00&time=lt.{today}T23:59:59&status=eq.false",
            headers=headers
        )
        em_preparo = response_em_preparo.json()
        response_prontos = await client.get(
            f"{SUPABASE_URL}/rest/v1/transactions?select=*,transaction_items(*)"
            f"&time=gte.{today}T00:00:00&time=lt.{today}T23:59:59&status=eq.true",
            headers=headers
        )
        prontos = response_prontos.json()
    return templates.TemplateResponse("dados.html", {
        "request": request,
        "em_preparo": em_preparo,
        "prontos": prontos
    })


@app.get("/api/dados", response_class=JSONResponse)
async def api_dados():
    today = datetime.now().strftime("%Y-%m-%d")
    async with httpx.AsyncClient() as client:
        response_em_preparo = await client.get(
            f"{SUPABASE_URL}/rest/v1/transactions?select=*,transaction_items(*)"
            f"&time=gte.{today}T00:00:00&time=lt.{today}T23:59:59&status=eq.false",
            headers=headers
        )
        em_preparo = response_em_preparo.json()
        response_prontos = await client.get(
            f"{SUPABASE_URL}/rest/v1/transactions?select=*,transaction_items(*)"
            f"&time=gte.{today}T00:00:00&time=lt.{today}T23:59:59&status=eq.true",
            headers=headers
        )
        prontos = response_prontos.json()
    return {"em_preparo": em_preparo, "prontos": prontos}
