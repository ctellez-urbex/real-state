"""
Model for bogota_data_lotes table.

This table contains lot information with geometry for Bogotá.
"""

from sqlalchemy import Column, Integer, String, Double
from geoalchemy2 import Geometry
from app.models.base import Base


class BogotaDataLotes(Base):
    """Model for bogota_data_lotes table."""
    
    __tablename__ = "bogota_data_lotes"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, comment="Primary key identifier")
    
    # Lot identification
    barmanpre = Column(String(12), nullable=True, comment="Barmanpre code - unique property identifier")
    manzcodigo = Column(String(9), nullable=True, comment="Block code identifier")
    
    # Coordinates
    latitud = Column(Double, nullable=True, comment="Latitude coordinate")
    longitud = Column(Double, nullable=True, comment="Longitude coordinate")
    
    # Geometry
    geometry = Column(Geometry, nullable=False, comment="Spatial geometry of the lot")
    
    def __repr__(self):
        """String representation of the model."""
        return f"<BogotaDataLotes({self._format_attrs()})>"
    
    def _format_attrs(self):
        """Format all column attributes for string representation."""
        return ', '.join(f"{col.name}={getattr(self, col.name)}" 
                        for col in self.__table__.columns)
