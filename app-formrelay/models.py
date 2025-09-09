from sqlalchemy import Column, BigInteger, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
# Importação corrigida (sem o '.')
from database import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    form_id = Column(String)
    name = Column(String)
    email = Column(String)
    message = Column(Text)
    ai_analysis = Column(JSONB)