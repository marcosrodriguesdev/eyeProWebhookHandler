import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DECIMAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Configuração do banco de dados
DATABASE_URL = os.getenv('SUPABASE_DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Definição das tabelas
class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, index=True)
    local_id = Column(Integer, index=True)
    status = Column(Boolean)
    time = Column(String)

    items = relationship("TransactionItem", back_populates="transaction")


class TransactionItem(Base):
    __tablename__ = 'transaction_items'
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    product_name = Column(String)
    price = Column(DECIMAL)
    quantity = Column(Integer)
    total = Column(DECIMAL)

    transaction = relationship("Transaction", back_populates="items")


# Criação das tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Inicialização do FastAPI
app = FastAPI()
templates = Jinja2Templates(directory="api/templates")


@app.post("/")
async def receber_dados(request: Request):
    session = SessionLocal()
    data = await request.json()

    transaction = Transaction(
        local_id=data['local_id'],
        status=data['status'],
        time=data['time']
    )
    session.add(transaction)
    session.commit()

    for item in data['transaction_items']:
        transaction_item = TransactionItem(
            transaction_id=transaction.id,
            product_name=item['product_name'],
            price=item['price'],
            quantity=item['quantity'],
            total=item['total']
        )
        session.add(transaction_item)

    session.commit()
    session.close()
    return {"status": "ok"}


@app.get("/dados", response_class=HTMLResponse)
async def exibir_dados(request: Request):
    session = SessionLocal()
    transactions = session.query(Transaction).all()
    session.close()
    return templates.TemplateResponse("dados.html", {"request": request, "transactions": transactions})
