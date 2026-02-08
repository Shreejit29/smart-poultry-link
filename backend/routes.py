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

@router.post("/order")
def place_order(qty: int, user_id: int):
    db = SessionLocal()

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    payment = process_payment(qty * 200)

    # Trust score update rule
    if payment["payment_status"] == "SUCCESS":
        user.trust = min(user.trust + 0.02, 1.0)
        order_status = "PAID"
    else:
        user.trust = max(user.trust - 0.05, 0.0)
        order_status = "FAILED"

    order = Order(
        qty=qty,
        user_id=user_id,
        status=order_status,
        payment_status=payment["payment_status"]
    )

    db.add(order)
    db.commit()

    return {
        "order_status": order_status,
        "payment_status": payment["payment_status"],
        "transaction_id": payment["transaction_id"],
        "updated_trust": user.trust
    }
