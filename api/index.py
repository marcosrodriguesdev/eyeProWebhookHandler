from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="api/templates")

# Armazena os dados recebidos (em memória)
dados_recebidos = {}


@app.post("/")
async def receber_dados(request: Request):
    global dados_recebidos
    dados_recebidos = await request.json()
    return {"status": "ok"}


@app.get("/dados", response_class=HTMLResponse)
async def exibir_dados(request: Request):
    return templates.TemplateResponse("dados.html", {"request": request, "dados": dados_recebidos})
