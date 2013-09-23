from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    DateTime,
)

# You will need to point this to wherever your declarative base is
from ..models import Base

class NimblescanCache(Base):
    __tablename__ = 'nimblescan_cache'
    user          = Column(Integer, ForeignKey("users.id"), nullable=False, primary_key=True)
    expires       = Column(DateTime, nullable=False)
    content       = Column(Text, nullable=False)
