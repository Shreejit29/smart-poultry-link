from fastapi import APIRouter, HTTPException
from database import SessionLocal
from models import User, Order
from auth import hash_password, verify_password, create_access_token
from payment_dummy import process_payment

router = APIRouter()


@router.post("/register")
def register(username: str, password: str, role: str):
    db = SessionLocal()

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        username=username,
        password=hash_password(password),
        role=role,
        trust=0.5
    )
    db.add(user)
    db.commit()

    return {"message": "User registered successfully"}


@router.post("/login")
def login(username: str, password: str):
    db = SessionLocal()

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        {"user_id": user.id, "role": user.role}
    )

    return {
        "access_token": token,
        "role": user.role,
        "trust": user.trust
    }


@router.post("/order")
def place_order(qty: int, user_id: int):
    db = SessionLocal()

    payment = process_payment(qty * 200)  # dummy pricing

    order = Order(
        qty=qty,
        user_id=user_id,
        status="PAID" if payment["payment_status"] == "SUCCESS" else "FAILED",
        payment_status=payment["payment_status"]
    )
    db.add(order)
    db.commit()

    return {
        "order_status": order.status,
        "payment_status": order.payment_status,
        "transaction_id": payment["transaction_id"]
    }
