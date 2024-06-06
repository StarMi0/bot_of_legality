from sqlalchemy import Column, String, Date, ForeignKey, TEXT, DATE, Integer, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    user_id = Column(String(255), primary_key=True)
    user_name = Column(String(255))
    user_fio = Column(String(255))
    user_date_birth = Column(String(255))
    registration_date = Column(DATE)
    role = Column(String(255), default='user')


class UserInfo(Base):
    __tablename__ = 'user_info'
    user_id = Column(String(255), ForeignKey('users.user_id'), primary_key=True)
    passport_serial = Column(String(255))
    passport_number = Column(String(255))
    checking_account = Column(String(255))
    user = relationship("User")


class LawyerInfo(Base):
    __tablename__ = 'lawyer_info'
    user_id = Column(String(255), ForeignKey('users.user_id'), primary_key=True)
    education = Column(String(255))
    education_documents = Column(TEXT)
    user = relationship("User")


class EducationDocument(Base):
    __tablename__ = 'education_documents'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), ForeignKey('users.user_id'))
    document = Column(TEXT)
    user = relationship("User")


class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(String(255), primary_key=True)
    user_id = Column(String(255), ForeignKey('users.user_id'))
    lawyer_id = Column(String(255), ForeignKey('users.user_id'))
    order_status = Column(String(255))
    group_id = Column(String(255))
    user = relationship("User", foreign_keys=[user_id])
    lawyer = relationship("User", foreign_keys=[lawyer_id])


class OrderInfo(Base):
    __tablename__ = 'orders_info'
    order_id = Column(String(255), ForeignKey('orders.order_id'), primary_key=True)
    order_text = Column(TEXT)
    documents_id = Column(TEXT)
    order_cost = Column(String(255))
    order_day_start = Column(DATE)
    order_day_end = Column(DATE)
    message_id = Column(String(255))
    group_id = Column(String(255))
    order = relationship("Order")


class Offer(Base):
    __tablename__ = 'offers'
    order_id = Column(String(255), ForeignKey('orders.order_id'), primary_key=True)
    lawyer_id = Column(String(255), ForeignKey('users.user_id'))
    order_cost = Column(String(255))
    develop_time = Column(String(255))
    order = relationship("Order")
    lawyer = relationship("User")
