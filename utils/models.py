from sqlalchemy import create_engine, Column, Integer, Float, String, Date, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PlaidAccount(Base):
    __tablename__ = "plaid_accounts"

    id = Column(Integer, primary_key=True, index=True)
    plaid_account_id = Column(String, unique=True, nullable=False)
    access_token = Column(String, nullable=False)
    account_name = Column(String)
    account_type = Column(String)
    institution_name = Column(String)
    last_sync = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    plaid_transaction_id = Column(String, unique=True, nullable=False)
    account_id = Column(Integer, ForeignKey('plaid_accounts.id'))
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String)
    merchant_name = Column(String)
    description = (String)

    account = relationship("PlaidAccount", backref="transactions")

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, default=datetime.utcnow)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String)

class Investment(Base):
    __tablename__ = "investments"
    
    id = Column(Integer, primary_key=True, index=True)
    asset = Column(String, nullable=False)
    current_value = Column(Float, nullable=False)
    initial_value = Column(Float, nullable=False)
    purchase_date = Column(Date, default=datetime.utcnow)

class FinancialGoal(Base):
    __tablename__ = "financial_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    target = Column(Float, nullable=False)
    current = Column(Float, nullable=False)
    deadline = Column(Date, nullable=False)

# Create all tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()