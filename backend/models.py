from sqlalchemy import Column, Integer, String, Float
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)   # consumer / admin
    trust = Column(Float, default=0.5)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    qty = Column(Integer, nullable=False)
    status = Column(String, nullable=False)          # PAID / FAILED
    payment_status = Column(String, nullable=False)  # SUCCESS / FAILED
    user_id = Column(Integer, nullable=False)
    farmer_id = Column(Integer, nullable=True)
class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)

    # Link to User table (login identity)
    user_id = Column(Integer, nullable=False, unique=True)

    # Supply-side attributes
    capacity_kg = Column(Integer, nullable=False)
    available_kg = Column(Integer, nullable=False)

    location = Column(String, nullable=False)

    # Operational status
    is_active = Column(Integer, default=1)  # 1 = active, 0 = offline

    # Performance metrics
    trust = Column(Float, default=0.5)
    acceptance_rate = Column(Float, default=1.0)
    sla_score = Column(Float, default=1.0)
