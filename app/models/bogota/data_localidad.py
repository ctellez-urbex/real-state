"""
Model for bogota_data_localidad table.

This table contains locality boundaries with geometry for Bogotá.
"""

from geoalchemy2 import Geometry
from sqlalchemy import Column, Double, Integer, String

from app.models.base import Base


class BogotaDataLocalidad(Base):
    """Model for bogota_data_localidad table."""

    __tablename__ = "bogota_data_localidad"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, comment="Primary key identifier")

    # Locality data
    locnombre = Column(String(18), nullable=True, comment="Locality name")
    locaadmini = Column(
        String(36), nullable=True, comment="Administrative locality name"
    )
    locarea = Column(Double, nullable=True, comment="Locality area in square meters")
    loccodigo = Column(String(2), nullable=True, comment="Locality code identifier")

    # Geometry
    geometry = Column(
        Geometry, nullable=False, comment="Spatial geometry of the locality boundary"
    )

    def __repr__(self):
        """String representation of the model."""
        return f"<BogotaDataLocalidad({self._format_attrs()})>"

    def _format_attrs(self):
        """Format all column attributes for string representation."""
        return ", ".join(
            f"{col.name}={getattr(self, col.name)}" for col in self.__table__.columns
        )
