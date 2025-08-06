"""
Model for bogota_grid_polygon table.

This table contains grid polygon information with geometry for Bogotá.
"""

from sqlalchemy import Column, Integer, Text
from geoalchemy2 import Geometry
from app.models.base import Base


class BogotaGridPolygon(Base):
    """Model for bogota_grid_polygon table."""
    
    __tablename__ = "bogota_grid_polygon"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, comment="Primary key identifier")
    
    # Grid identification
    idmap = Column(Integer, nullable=True, comment="Map ID identifier")
    barmanpre = Column(Text, nullable=True, comment="Barmanpre codes within the grid polygon")
    
    # Geometry
    geometry = Column(Geometry, nullable=False, comment="Spatial geometry of the grid polygon")
    
    def __repr__(self):
        """String representation of the model."""
        return f"<BogotaGridPolygon({self._format_attrs()})>"
    
    def _format_attrs(self):
        """Format all column attributes for string representation."""
        return ', '.join(f"{col.name}={getattr(self, col.name)}" 
                        for col in self.__table__.columns)
