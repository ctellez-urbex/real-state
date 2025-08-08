"""
Model for bogota_data_barrio_catastral table.

This table contains neighborhood boundaries with geometry for Bogotá.
"""

from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String

from app.models.base import Base


class BogotaDataBarrioCatastral(Base):
    """Model for bogota_data_barrio_catastral table."""

    __tablename__ = "bogota_data_barrio_catastral"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, comment="Primary key identifier")

    # Neighborhood data
    scacodigo = Column(String(6), nullable=True, comment="Neighborhood code identifier")
    scatipo = Column(Integer, nullable=True, comment="Neighborhood type code")
    scanombre = Column(String(33), nullable=True, comment="Neighborhood name")

    # Geometry
    geometry = Column(
        Geometry,
        nullable=False,
        comment="Spatial geometry of the neighborhood boundary",
    )

    def __repr__(self):
        """String representation of the model."""
        return f"<BogotaDataBarrioCatastral({self._format_attrs()})>"

    def _format_attrs(self):
        """Format all column attributes for string representation."""
        return ", ".join(
            f"{col.name}={getattr(self, col.name)}" for col in self.__table__.columns
        )
