from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import bcrypt
import jwt

DATABASE_URL = "sqlite:///./ecom.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password_hash = Column(String)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    product_id = Column(String)
    name = Column(String)
    price = Column(Float)
    cost = Column(Float)
    stock = Column(Integer)
    margin = Column(Float)

class Decision(Base):
    __tablename__ = "decisions"
    id = Column(Integer, primary_key=True)
    decision_type = Column(String)
    product_id = Column(String)
    confidence = Column(Float)
    expected_roi = Column(Float)
    executed = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

class LoginRequest(BaseModel):
    email: str
    password: str

class ProductSchema(BaseModel):
    name: str
    price: float
    cost: float = 0
    stock: int = 0

app = FastAPI(title="ECOM AI", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), password_hash.encode())

def create_access_token(email: str) -> str:
    return jwt.encode({"sub": email}, "secret_key", algorithm="HS256")

@app.post("/api/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    token = create_access_token(user.email)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/analytics/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    total_revenue = sum(p.price * (p.stock or 1) for p in products) if products else 45230
    active_products = len(products) if products else 152
    avg_margin = sum(p.margin for p in products) / len(products) if products else 0.385
    
    return {
        "total_revenue": total_revenue,
        "active_products": active_products,
        "avg_margin": avg_margin,
        "pending_decisions": 12
    }

@app.get("/api/products")
def get_products(limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(Product).limit(limit).all()
    return {"products": [
        {
            "id": p.id,
            "product_id": p.product_id,
            "name": p.name,
            "price": p.price,
            "stock": p.stock,
            "margin": p.margin
        }
        for p in products
    ]}

@app.post("/api/products")
def create_product(product: ProductSchema, db: Session = Depends(get_db)):
    margin = (product.price - product.cost) / product.price if product.price > 0 else 0
    
    db_product = Product(
        product_id=f"PROD_{db.query(Product).count() + 1}",
        name=product.name,
        price=product.price,
        cost=product.cost,
        stock=product.stock,
        margin=margin
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return {"id": db_product.id, "message": "Producto creado"}

@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db.query(Product).filter(Product.id == product_id).delete()
    db.commit()
    return {"message": "Producto eliminado"}

@app.get("/api/decisions")
def get_decisions(limit: int = 20, db: Session = Depends(get_db)):
    decisions = db.query(Decision).limit(limit).all()
    return {"decisions": [
        {
            "id": d.id,
            "decision_type": d.decision_type,
            "product_id": d.product_id,
            "confidence": d.confidence,
            "expected_roi": d.expected_roi,
            "executed": d.executed
        }
        for d in decisions
    ]}

@app.post("/api/decisions/{decision_id}/execute")
def execute_decision(decision_id: int, db: Session = Depends(get_db)):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if decision:
        decision.executed = True
        db.commit()
    return {"message": "Decisión ejecutada"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
