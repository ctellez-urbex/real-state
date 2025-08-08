"""
Model for bogota_data_lotes_fastsearch table.

This table contains fast search lot information with geometry for Bogotá.
"""

from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String

from app.models.base import Base


class BogotaDataLotesFastsearch(Base):
    """Model for bogota_data_lotes_fastsearch table."""

    __tablename__ = "bogota_data_lotes_fastsearch"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, comment="Primary key identifier")

    # Lot identification
    barmanpre = Column(
        String(12), nullable=True, comment="Barmanpre code - unique property identifier"
    )
    manzcodigo = Column(String(9), nullable=True, comment="Block code identifier")

    # Geometry
    geometry = Column(
        Geometry, nullable=False, comment="Spatial geometry of the lot for fast search"
    )

    def __repr__(self):
        """String representation of the model."""
        return f"<BogotaDataLotesFastsearch({self._format_attrs()})>"

    def _format_attrs(self):
        """Format all column attributes for string representation."""
        return ", ".join(
            f"{col.name}={getattr(self, col.name)}" for col in self.__table__.columns
        )
