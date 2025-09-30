from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Define the SQLAlchemy model for your table
Base = declarative_base()

class Historian(Base):
    __tablename__ = 'historian'
    #to update columns
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100), unique=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}
