from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

db_user = os.getenv("DATABASE_USER", "user")
db_password = os.getenv("DATABASE_PASSWORD", "password")
db_host = os.getenv("DATABASE_HOST", "localhost")
db_port = os.getenv("DATABASE_PORT", 5432)
db_name = os.getenv("DATABASE_NAME", "database")

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)