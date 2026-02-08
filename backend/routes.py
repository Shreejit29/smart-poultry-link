from fastapi import APIRouter, HTTPException
from database import SessionLocal
from models import User, Order
from auth import hash_password, verify_password, create_access_token
from payment_dummy import process_payment
from models import User, Order, Farmer
router = APIRouter()


# ------------------------
# USER REGISTRATION
# ------------------------
@router.post("/register")
def register(username: str, password: str, role: str):
    db = SessionLocal()
    try:
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

    finally:
        db.close()


# ------------------------
# USER LOGIN
# ------------------------
@router.post("/login")
def login(username: str, password: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token(
            {"user_id": user.id, "role": user.role}
        )

        return {
            "access_token": token,
            "role": user.role,
            "trust": user.trust
        }

    finally:
        db.close()


# ------------------------
# PLACE ORDER (WITH TRUST LOGIC)
# ------------------------
@router.post("/order")
def place_order(qty: int, user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 🚫 Hard block for very low trust users
        if user.trust < 0.2:
            raise HTTPException(
                status_code=403,
                detail="User trust too low. Ordering temporarily disabled."
            )

        # Dummy payment
        payment = process_payment(qty * 200)

        # Trust update rules
        if payment["payment_status"] == "SUCCESS":
            user.trust = min(user.trust + 0.02, 1.0)
            order_status = "PAID"
        else:
            user.trust = max(user.trust - 0.05, 0.0)
            order_status = "FAILED"

        order = Order(
            qty=qty,
            user_id=user.id,
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

    finally:
        db.close()
# ------------------------
# FARMER REGISTRATION
# ------------------------
@router.post("/farmer/register")
def register_farmer(
    user_id: int,
    capacity_kg: int,
    location: str
):
    db = SessionLocal()
    try:
        # Check user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check farmer already exists
        existing_farmer = db.query(Farmer).filter(Farmer.user_id == user_id).first()
        if existing_farmer:
            raise HTTPException(
                status_code=400,
                detail="Farmer profile already exists for this user"
            )

        farmer = Farmer(
            user_id=user_id,
            capacity_kg=capacity_kg,
            available_kg=capacity_kg,
            location=location,
            is_active=1,
            trust=0.5,
            acceptance_rate=1.0,
            sla_score=1.0
        )

        db.add(farmer)
        db.commit()

        return {
            "message": "Farmer registered successfully",
            "farmer_id": farmer.id,
            "capacity_kg": farmer.capacity_kg,
            "location": farmer.location
        }

    finally:
        db.close()
# ------------------------
# FARMER DASHBOARD (VIEW METRICS)
# ------------------------
@router.get("/farmer/dashboard")
def farmer_dashboard(user_id: int):
    db = SessionLocal()
    try:
        farmer = db.query(Farmer).filter(Farmer.user_id == user_id).first()
        if not farmer:
            raise HTTPException(
                status_code=404,
                detail="Farmer profile not found for this user"
            )

        return {
            "farmer_id": farmer.id,
            "user_id": farmer.user_id,
            "capacity_kg": farmer.capacity_kg,
            "available_kg": farmer.available_kg,
            "location": farmer.location,
            "is_active": bool(farmer.is_active),
            "trust": farmer.trust,
            "acceptance_rate": farmer.acceptance_rate,
            "sla_score": farmer.sla_score
        }

    finally:
        db.close()
