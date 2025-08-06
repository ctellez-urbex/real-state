"""
Model for bogota_data_andenes table.

This table contains sidewalk information for Bogotá.
"""

from sqlalchemy import Column, Integer
from geoalchemy2 import Geometry
from app.models.base import Base


class BogotaDataAndenes(Base):
    """Model for bogota_data_andenes table."""
    
    __tablename__ = "bogota_data_andenes"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, comment="Primary key identifier")
    
    # Sidewalk data
    andmateria = Column(Integer, nullable=True, comment="Sidewalk material type code")
    andcodigo = Column(Integer, nullable=True, comment="Sidewalk code identifier")
    andciv = Column(Integer, nullable=True, comment="Civil works code for sidewalk")
    
    # Geometry
    geometry = Column(Geometry, nullable=False, comment="Spatial geometry of the sidewalk")
    
    def __repr__(self):
        """String representation of the model."""
        return f"<BogotaDataAndenes({self._format_attrs()})>"
    
    def _format_attrs(self):
        """Format all column attributes for string representation."""
        return ', '.join(f"{col.name}={getattr(self, col.name)}" 
                        for col in self.__table__.columns) 
