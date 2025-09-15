import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Pega a string de conexão do banco de dados do arquivo .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Cria o "motor" de conexão com o banco de dados
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Cria uma fábrica de sessões para conversar com o banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Uma classe base para nossos modelos de tabela
Base = declarative_base()