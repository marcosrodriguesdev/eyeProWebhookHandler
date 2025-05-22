from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="api/templates")


@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("dados.html", {"request": request, "dados": None})


@app.post("/", response_class=HTMLResponse)
async def exibir_dados(request: Request):
    json_data = await request.json()
    return templates.TemplateResponse("dados.html", {"request": request, "dados": json_data})
