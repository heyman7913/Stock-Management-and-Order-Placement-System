from models.Base import *


class CustomerLogin(Base):
    __tablename__ = "customer_login"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer_details = relationship("CustomerDetails", uselist=False, back_populates="parent")
    customer_sales = relationship("CustomerSales", uselist=False, back_populates="parent")

    def __repr__(self):
        return f"{self.email}"


class CustomerDetails(Base):
    __tablename__ = "customer_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phoneNumber = Column(Integer, nullable=False)
    emailID = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer_login_id = mapped_column(Integer,
                                      ForeignKey(
                                          "customer_login.id",
                                          ondelete="CASCADE"),
                                      nullable=False)
    customer_login = relationship("CustomerLogin", back_populates="child")

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"


class CustomerSales(Base):
    __tablename__ = "customer_sales"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer_login_id = mapped_column(Integer,
                                     ForeignKey(
                                         "customer_login.id",
                                         ondelete="CASCADE"),
                                     nullable=False)
    customer_login = relationship("CustomerLogin", back_populates="child")
