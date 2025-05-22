from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("dados.html", {"request": request, "dados": None})


@app.post("/", response_class=HTMLResponse)
async def form_post(request: Request, nome: str = Form(...), idade: int = Form(...)):
    dados = {"nome": nome, "idade": idade}
    return templates.TemplateResponse("dados.html", {"request": request, "dados": dados})
