from sqlalchemy import Column, Integer, String, VARCHAR, DateTime, TIMESTAMP, text, JSON
from sqlalchemy.dialects.mysql import INTEGER, insert
from Base import Base
from engine import engine

class CustomerDetails(Base):
    __tablename__ = "CustomerDetails"
    customerID = Column(INTEGER, primary_key=True, autoincrement=True)
    customerFirstName = Column(String(50), nullable=False)
    customerLastName = Column(String(50), nullable=False)
    phoneNumber = Column(INTEGER, nullable=False)
    emailID = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    salesCount = Column(INTEGER, nullable=False)