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
