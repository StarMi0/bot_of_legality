from sqlalchemy import Column, String, ForeignKey, TEXT, DATE, Integer
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    user_id = Column(String(255), primary_key=True)
    user_name = Column(String(255))
    user_fio = Column(String(255))
    user_date_birth = Column(String(255))
    registration_date = Column(DATE)
    role = Column(String(255), default='user')

    orders_as_user = relationship("Order", foreign_keys="[Order.user_id]", back_populates="user")
    orders_as_lawyer = relationship("Order", foreign_keys="[Order.lawyer_id]", back_populates="lawyer")
    offers = relationship("Offer", back_populates="lawyer")
    user_info = relationship("UserInfo", uselist=False, back_populates="user")
    lawyer_info = relationship("LawyerInfo", uselist=False, back_populates="user")
    education_documents = relationship("EducationDocument", back_populates="user")


class UserInfo(Base):
    __tablename__ = 'user_info'
    user_id = Column(String(255), ForeignKey('users.user_id'), primary_key=True)
    passport_serial = Column(String(255))
    passport_number = Column(String(255))
    checking_account = Column(String(255))

    user = relationship("User", back_populates="user_info")


class LawyerInfo(Base):
    __tablename__ = 'lawyer_info'
    user_id = Column(String(255), ForeignKey('users.user_id'), primary_key=True)
    education = Column(String(255))

    user = relationship("User", back_populates="lawyer_info")


class EducationDocument(Base):
    __tablename__ = 'education_documents'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), ForeignKey('users.user_id'))
    document = Column(TEXT)

    user = relationship("User", back_populates="education_documents")


class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(String(255), primary_key=True)
    user_id = Column(String(255), ForeignKey('users.user_id'))
    lawyer_id = Column(String(255), ForeignKey('users.user_id'))
    order_status = Column(String(255))
    group_id = Column(String(255))

    user = relationship("User", foreign_keys=[user_id], back_populates="orders_as_user")
    lawyer = relationship("User", foreign_keys=[lawyer_id], back_populates="orders_as_lawyer")
    orders_info = relationship("OrderInfo", uselist=False, back_populates="order")
    offers = relationship("Offer", back_populates="order")


class OrderInfo(Base):
    __tablename__ = 'orders_info'
    order_id = Column(String(255), ForeignKey('orders.order_id'), primary_key=True)
    order_text = Column(TEXT)
    order_cost = Column(String(255))
    order_day_start = Column(DATE)
    order_day_end = Column(DATE)
    order_day_end_actually = Column(DATE)
    message_id = Column(String(255))
    group_id = Column(String(255))

    order = relationship("Order", back_populates="orders_info")
    documents = relationship("OrderDocuments", back_populates="order_info")


class Offer(Base):
    __tablename__ = 'offers'
    offer_id = Column(String(255), primary_key=True)
    order_id = Column(String(255), ForeignKey('orders.order_id'))
    lawyer_id = Column(String(255), ForeignKey('users.user_id'))
    order_cost = Column(String(255))
    develop_time = Column(String(255))

    order = relationship("Order", back_populates="offers")
    lawyer = relationship("User", back_populates="offers")


class OrderDocuments(Base):
    __tablename__ = 'orders_documents'
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(255))
    order_id = Column(String(255), ForeignKey('orders_info.order_id'))

    order_info = relationship("OrderInfo", back_populates="documents")
