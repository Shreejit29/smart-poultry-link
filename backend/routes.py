from fastapi import APIRouter, HTTPException
from database import SessionLocal
from models import User, Order
from auth import hash_password, verify_password, create_access_token
from payment_dummy import process_payment
from models import User, Order, Farmer
router = APIRouter()
from models import User, Order, Farmer

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
# ------------------------
# FARMER AVAILABILITY TOGGLE
# ------------------------
@router.post("/farmer/availability")
def toggle_farmer_availability(user_id: int, is_active: int):
    db = SessionLocal()
    try:
        farmer = db.query(Farmer).filter(Farmer.user_id == user_id).first()
        if not farmer:
            raise HTTPException(
                status_code=404,
                detail="Farmer profile not found"
            )

        if is_active not in (0, 1):
            raise HTTPException(
                status_code=400,
                detail="is_active must be 0 (offline) or 1 (online)"
            )

        farmer.is_active = is_active
        db.commit()

        return {
            "message": "Availability updated",
            "is_active": bool(farmer.is_active)
        }

    finally:
        db.close()
# ------------------------
# ORDER ASSIGNMENT (SYSTEM)
# ------------------------
@router.post("/order/assign")
def assign_order(order_id: int):
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.status != "PAID":
            raise HTTPException(
                status_code=400,
                detail="Order not eligible for assignment"
            )

        # Select best available farmer (simple logic)
        farmer = (
            db.query(Farmer)
            .filter(Farmer.is_active == 1)
            .order_by(Farmer.trust.desc())
            .first()
        )

        if not farmer:
            raise HTTPException(
                status_code=404,
                detail="No active farmers available"
            )

        order.farmer_id = farmer.id
        order.status = "ASSIGNED"
        db.commit()

        return {
            "message": "Order assigned",
            "order_id": order.id,
            "farmer_id": farmer.id
        }

    finally:
        db.close()
# ------------------------
# FARMER ACCEPT / REJECT ORDER
# ------------------------
@router.post("/farmer/order/decision")
def farmer_decision(
    farmer_id: int,
    order_id: int,
    decision: str  # ACCEPT / REJECT
):
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.farmer_id != farmer_id:
            raise HTTPException(
                status_code=403,
                detail="Order not assigned to this farmer"
            )

        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer not found")

        if decision == "ACCEPT":
            order.status = "ACCEPTED"

            # Improve acceptance rate slightly
            farmer.acceptance_rate = min(farmer.acceptance_rate + 0.02, 1.0)

        elif decision == "REJECT":
            order.status = "REJECTED"
            order.farmer_id = None

            # Penalties
            farmer.trust = max(farmer.trust - 0.05, 0.0)
            farmer.acceptance_rate = max(farmer.acceptance_rate - 0.1, 0.0)

        else:
            raise HTTPException(
                status_code=400,
                detail="Decision must be ACCEPT or REJECT"
            )

        db.commit()

        return {
            "order_id": order.id,
            "decision": decision,
            "updated_trust": farmer.trust,
            "acceptance_rate": farmer.acceptance_rate
        }

    finally:
        db.close()
# ------------------------
# FARMER ORDER INBOX
# ------------------------
@router.get("/farmer/orders")
def farmer_orders(farmer_id: int):
    db = SessionLocal()
    try:
        orders = (
            db.query(Order)
            .filter(Order.farmer_id == farmer_id)
            .filter(Order.status == "ASSIGNED")
            .all()
        )

        return [
            {
                "order_id": o.id,
                "qty": o.qty,
                "status": o.status
            }
            for o in orders
        ]

    finally:
        db.close()
# ========================
# ADMIN DASHBOARD APIs
# ========================

@router.get("/admin/users")
def admin_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return [
            {
                "user_id": u.id,
                "username": u.username,
                "role": u.role,
                "trust": u.trust
            }
            for u in users
        ]
    finally:
        db.close()


@router.get("/admin/farmers")
def admin_farmers():
    db = SessionLocal()
    try:
        farmers = db.query(Farmer).all()
        return [
            {
                "farmer_id": f.id,
                "user_id": f.user_id,
                "capacity_kg": f.capacity_kg,
                "available_kg": f.available_kg,
                "location": f.location,
                "is_active": bool(f.is_active),
                "trust": f.trust,
                "acceptance_rate": f.acceptance_rate,
                "sla_score": f.sla_score
            }
            for f in farmers
        ]
    finally:
        db.close()


@router.get("/admin/orders")
def admin_orders():
    db = SessionLocal()
    try:
        orders = db.query(Order).all()
        return [
            {
                "order_id": o.id,
                "user_id": o.user_id,
                "farmer_id": o.farmer_id,
                "qty": o.qty,
                "status": o.status,
                "payment_status": o.payment_status
            }
            for o in orders
        ]
    finally:
        db.close()
# ========================
# ADMIN CONTROLS
# ========================

@router.post("/admin/user/trust")
def admin_update_user_trust(user_id: int, trust: float):
    db = SessionLocal()
    try:
        if trust < 0.0 or trust > 1.0:
            raise HTTPException(status_code=400, detail="Trust must be between 0 and 1")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.trust = trust
        db.commit()

        return {"message": "User trust updated", "trust": user.trust}
    finally:
        db.close()


@router.post("/admin/user/block")
def admin_block_user(user_id: int, is_blocked: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.is_blocked = is_blocked
        db.commit()

        return {
            "message": "User block status updated",
            "is_blocked": bool(user.is_blocked)
        }
    finally:
        db.close()


@router.post("/admin/farmer/trust")
def admin_update_farmer_trust(farmer_id: int, trust: float):
    db = SessionLocal()
    try:
        if trust < 0.0 or trust > 1.0:
            raise HTTPException(status_code=400, detail="Trust must be between 0 and 1")

        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer not found")

        farmer.trust = trust
        db.commit()

        return {"message": "Farmer trust updated", "trust": farmer.trust}
    finally:
        db.close()


@router.post("/admin/farmer/block")
def admin_block_farmer(farmer_id: int, is_blocked: int):
    db = SessionLocal()
    try:
        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer not found")

        farmer.is_blocked = is_blocked
        db.commit()

        return {
            "message": "Farmer block status updated",
            "is_blocked": bool(farmer.is_blocked)
        }
    finally:
        db.close()
