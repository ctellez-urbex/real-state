"""
Model for bogota_galeria_precios table.

This table contains price gallery information for Bogotá.
"""

from sqlalchemy import Column, Double, Integer

from app.models.base import Base


class BogotaGaleriaPrecios(Base):
    """Model for bogota_galeria_precios table."""

    __tablename__ = "bogota_galeria_precios"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, comment="Primary key identifier")

    # Property identification
    codinmueble = Column(Integer, nullable=True, comment="Property code identifier")
    codproyecto = Column(Integer, nullable=True, comment="Project code identifier")

    # Time period
    ano = Column(Integer, nullable=True, comment="Year of the price record")
    mes = Column(Integer, nullable=True, comment="Month of the price record (1-12)")

    # Price values in different currencies
    valor_N = Column(
        Double, nullable=True, comment="Price value in Colombian Pesos (COP)"
    )
    valor_D = Column(Double, nullable=True, comment="Price value in US Dollars (USD)")
    valor_P = Column(Double, nullable=True, comment="Price value in another currency")

    def __repr__(self):
        """String representation of the model."""
        return f"<BogotaGaleriaPrecios({self._format_attrs()})>"

    def _format_attrs(self):
        """Format all column attributes for string representation."""
        return ", ".join(
            f"{col.name}={getattr(self, col.name)}" for col in self.__table__.columns
        )
