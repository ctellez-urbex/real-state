"""
Model for bogota_lotes_normativa table.

This table contains normative information for lots in Bogotá.
"""

from sqlalchemy import Column, Integer, DateTime, Text
from app.models.base import Base


class BogotaLotesNormativa(Base):
    """Model for bogota_lotes_normativa table."""
    
    __tablename__ = "bogota_lotes_normativa"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, comment="Primary key identifier")
    
    # Normative data
    lista = Column(Text, nullable=True, comment="List of normative codes and regulations")
    pisos = Column(Integer, nullable=True, comment="Maximum number of floors allowed")
    altura_min_pot = Column(Integer, nullable=True, comment="Minimum height according to POT (Plan de Ordenamiento Territorial)")
    tratamiento = Column(Integer, nullable=True, comment="Urban treatment type code")
    actuacion_estrategica = Column(Integer, nullable=True, comment="Strategic action code")
    area_de_actividad = Column(Integer, nullable=True, comment="Activity area code")
    numero_propietarios = Column(Integer, nullable=True, comment="Number of property owners")
    via_principal = Column(Integer, nullable=True, comment="Main road indicator (1=main road, 0=secondary)")
    
    # Metadata
    fecha_update = Column(DateTime, nullable=True, comment="Last update date of normative information")
    
    def __repr__(self):
        """String representation of the model."""
        return f"<BogotaLotesNormativa({self._format_attrs()})>"
    
    def _format_attrs(self):
        """Format all column attributes for string representation."""
        return ', '.join(f"{col.name}={getattr(self, col.name)}" 
                        for col in self.__table__.columns) 
