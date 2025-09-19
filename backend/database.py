from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 👇 Replace with your correct SQL Server settings
DATABASE_URL = "mssql+pyodbc://@PRINCY\\MSSQL/CabBookingDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"

# Create engine
engine = create_engine(DATABASE_URL)

# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
