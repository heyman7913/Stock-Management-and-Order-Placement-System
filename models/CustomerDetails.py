from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import INTEGER
from models.Base import Base


class CustomerDetails(Base):
    __tablename__ = "CustomerDetails"
    customerID = Column(INTEGER, primary_key=True, autoincrement=True)
    customerFirstName = Column(String(50), nullable=False)
    customerLastName = Column(String(50), nullable=False)
    phoneNumber = Column(INTEGER, nullable=False)
    emailID = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    salesCount = Column(INTEGER, nullable=False)

# Model - Customer details