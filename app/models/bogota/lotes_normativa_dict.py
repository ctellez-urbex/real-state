"""
Model for bogota_lotes_normativa_dict table.

This table contains dictionary mappings for normative variables in Bogotá.
"""

from sqlalchemy import Column, Integer, String
from app.models.base import Base


class BogotaLotesNormativaDict(Base):
    """Model for bogota_lotes_normativa_dict table."""
    
    __tablename__ = "bogota_lotes_normativa_dict"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, comment="Primary key identifier")
    
    # Dictionary data
    variable = Column(String(21), nullable=True, comment="Variable name for normative mapping")
    indice = Column(Integer, nullable=True, comment="Index value for the variable")
    input = Column(String(155), nullable=True, comment="Input value or description for the variable")
    
    # Metadata
    fecha_update = Column(String(10), nullable=True, comment="Last update date of dictionary entry")
    
    def __repr__(self):
        """String representation of the model."""
        return f"<BogotaLotesNormativaDict({self._format_attrs()})>"
    
    def _format_attrs(self):
        """Format all column attributes for string representation."""
        return ', '.join(f"{col.name}={getattr(self, col.name)}" 
                        for col in self.__table__.columns) 