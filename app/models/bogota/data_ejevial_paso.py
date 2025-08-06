"""
Model for bogota_data_ejevial_paso table.

This table contains road axis and passage information for Bogotá.
"""

from sqlalchemy import Column, Integer, String, Text
from geoalchemy2 import Geometry
from app.models.base import Base


class BogotaDataEjevialPaso(Base):
    """Model for bogota_data_ejevial_paso table."""
    
    __tablename__ = "bogota_data_ejevial_paso"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, comment="Primary key identifier")
    
    # Road identification
    objectid = Column(Integer, nullable=True, comment="Object ID from GIS system")
    codigo_id = Column(String(4), nullable=True, comment="Road code identifier")
    nombre = Column(String(67), nullable=True, comment="Road name")
    
    # Road classification
    clasificac = Column(Integer, nullable=True, comment="Road classification code")
    tipo_via = Column(String(4), nullable=True, comment="Road type")
    clasific_1 = Column(String(4), nullable=True, comment="Secondary classification")
    estado_via = Column(Integer, nullable=True, comment="Road state/condition")
    
    # Administrative information
    acto_admin = Column(String(3), nullable=True, comment="Administrative act code")
    numero_act = Column(String(3), nullable=True, comment="Act number")
    fecha_acto = Column(String(10), nullable=True, comment="Act date")
    normativa = Column(String(146), nullable=True, comment="Regulatory framework")
    
    # Technical details
    observacio = Column(String(4), nullable=True, comment="Observations")
    escala_cap = Column(String(4), nullable=True, comment="Capture scale")
    fecha_capt = Column(String(10), nullable=True, comment="Capture date")
    responsabl = Column(String(2), nullable=True, comment="Responsible entity")
    
    # Geometry
    delgeometry = Column(Text, nullable=True, comment="Geometry description")
    geometry = Column(Geometry, nullable=True, comment="Spatial geometry of the road axis")
    
    def __repr__(self):
        """String representation of the model."""
        return f"<BogotaDataEjevialPaso({self._format_attrs()})>"
    
    def _format_attrs(self):
        """Format all column attributes for string representation."""
        return ', '.join(f"{col.name}={getattr(self, col.name)}" 
                        for col in self.__table__.columns)
