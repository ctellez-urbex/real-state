"""
Model for bogota_data_construcciones table.

This table contains construction information for properties in Bogotá.
"""

from geoalchemy2 import Geometry
from sqlalchemy import Column, Double, Integer, String

from app.models.base import Base


class BogotaDataConstrucciones(Base):
    """Model for bogota_data_construcciones table."""

    __tablename__ = "bogota_data_construcciones"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, comment="Primary key identifier")

    # Construction data
    concodigo = Column(
        String(25), nullable=True, comment="Construction code identifier"
    )
    connpisos = Column(
        Integer, nullable=True, comment="Number of floors in the construction"
    )
    contsemis = Column(Integer, nullable=True, comment="Number of semi-basement floors")
    connsotano = Column(Integer, nullable=True, comment="Number of basement floors")
    barmanpre = Column(
        String(12), nullable=True, comment="Barmanpre code linking to property"
    )
    conmejora = Column(
        Integer, nullable=True, comment="Improvement code for construction"
    )
    convoladiz = Column(Integer, nullable=True, comment="Voladizo (overhang) code")
    conaltura = Column(Double, nullable=True, comment="Construction height in meters")
    conelevaci = Column(Integer, nullable=True, comment="Number of elevator floors")
    geometry = Column(
        Geometry, nullable=False, comment="Spatial geometry of the construction"
    )

    def __repr__(self):
        """String representation of the model."""
        return f"<BogotaDataConstrucciones({self._format_attrs()})>"

    def _format_attrs(self):
        """Format all column attributes for string representation."""
        return ", ".join(
            f"{col.name}={getattr(self, col.name)}" for col in self.__table__.columns
        )
