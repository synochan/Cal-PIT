import os
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Get database URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Create SQLAlchemy engine and session
if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
else:
    engine = None
    Session = None
Base = declarative_base()

class FunctionEntry(Base):
    """
    Model for storing function entries in the database.
    """
    __tablename__ = "function_entries"
    
    id = Column(Integer, primary_key=True)
    function_text = Column(String(255), nullable=False)
    latex_representation = Column(Text)
    x_min = Column(Float, nullable=False)
    x_max = Column(Float, nullable=False)
    show_derivative = Column(sa.Boolean, default=True)
    derivative_order = Column(Integer, default=1)
    show_integral = Column(sa.Boolean, default=True)
    ai_explanation = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<FunctionEntry(id={self.id}, function_text='{self.function_text}')>"

# Create tables if they don't exist
def init_db():
    Base.metadata.create_all(engine)

# Function to get the database session
def get_db_session():
    if Session:
        return Session()
    return None

# Function to save a function entry to the database
def save_function_entry(
    function_text, 
    latex_representation, 
    x_min, 
    x_max, 
    show_derivative=True,
    derivative_order=1,
    show_integral=True,
    ai_explanation=None
):
    session = get_db_session()
    if not session:
        return None
    
    entry = FunctionEntry(
        function_text=function_text,
        latex_representation=latex_representation,
        x_min=x_min,
        x_max=x_max,
        show_derivative=show_derivative,
        derivative_order=derivative_order,
        show_integral=show_integral,
        ai_explanation=ai_explanation
    )
    session.add(entry)
    session.commit()
    entry_id = entry.id
    session.close()
    return entry_id

# Function to get all function entries
def get_all_function_entries(limit=10):
    session = get_db_session()
    if not session:
        return []
    
    entries = session.query(FunctionEntry).order_by(FunctionEntry.timestamp.desc()).limit(limit).all()
    session.close()
    return entries

# Function to get a specific function entry by ID
def get_function_entry(entry_id):
    session = get_db_session()
    if not session:
        return None
    
    entry = session.query(FunctionEntry).filter(FunctionEntry.id == entry_id).first()
    session.close()
    return entry

# Initialize the database
if engine:
    init_db()