"""
Model for bogota_data_calzada table.

This table contains road/street information with geometry for Bogotá.
"""

from sqlalchemy import Column, Integer, Double
from geoalchemy2 import Geometry
from app.models.base import Base


class BogotaDataCalzada(Base):
    """Model for bogota_data_calzada table."""
    
    __tablename__ = "bogota_data_calzada"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, comment="Primary key identifier")
    
    # Road data
    calfuncion = Column(Integer, nullable=True, comment="Road function code")
    caltsuperf = Column(Integer, nullable=True, comment="Road surface type code")
    calcodigo = Column(Integer, nullable=True, comment="Road code identifier")
    calciv = Column(Integer, nullable=True, comment="Civil works code for road")
    
    # Road measurements
    calancho = Column(Double, nullable=True, comment="Road width in meters")
    callongitu = Column(Double, nullable=True, comment="Road length in meters")
    
    # Geometry
    geometry = Column(Geometry, nullable=False, comment="Spatial geometry of the road")
    
    def __repr__(self):
        """String representation of the model."""
        return f"<BogotaDataCalzada({self._format_attrs()})>"
    
    def _format_attrs(self):
        """Format all column attributes for string representation."""
        return ', '.join(f"{col.name}={getattr(self, col.name)}" 
                        for col in self.__table__.columns) 
