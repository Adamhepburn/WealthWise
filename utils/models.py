from sqlalchemy import create_engine, Column, Integer, Float, String, Date, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import QueuePool
import os
from datetime import datetime
import time

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

# Configure engine with connection pooling and retry
def create_db_engine():
    return create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,  # Recycle connections after 30 minutes
        connect_args={
            "connect_timeout": 30,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5
        }
    )

# Initialize engine with retry logic
def get_engine():
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            engine = create_db_engine()
            # Test connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return engine
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"Database connection attempt {attempt + 1} failed, retrying in {retry_delay}s...")
            time.sleep(retry_delay)
            retry_delay *= 2

engine = get_engine()
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
    description = Column(String)

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