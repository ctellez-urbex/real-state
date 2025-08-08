"""
Model for bogota_data_caracteristicas table.

This table contains property characteristics and cadastral data for Bogotá.
"""

from sqlalchemy import Column, Double, Integer, String, Text

from app.models.base import Base


class BogotaDataCaracteristicas(Base):
    """Model for bogota_data_caracteristicas table."""

    __tablename__ = "bogota_data_caracteristicas"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, comment="Primary key identifier")
    barmanpre = Column(
        String(12), nullable=True, comment="Barmanpre code - unique property identifier"
    )

    # Area measurements
    preaconst = Column(
        Double, nullable=True, comment="Construction area in square meters"
    )
    preaterre = Column(Double, nullable=True, comment="Land area in square meters")

    # Age information
    prevetustzmin = Column(
        Integer, nullable=True, comment="Minimum age of the property in years"
    )
    prevetustzmax = Column(
        Integer, nullable=True, comment="Maximum age of the property in years"
    )

    # Socioeconomic and property data
    estrato = Column(Double, nullable=True, comment="Socioeconomic stratum (1-6)")
    predios = Column(Integer, nullable=True, comment="Number of properties in the lot")

    # Construction details
    connpisos = Column(
        Double, nullable=True, comment="Number of floors in the construction"
    )
    connsotano = Column(Double, nullable=True, comment="Number of basement floors")
    contsemis = Column(Double, nullable=True, comment="Number of semi-basement floors")
    conelevaci = Column(Double, nullable=True, comment="Number of elevator floors")

    # Address and location
    formato_direccion = Column(
        Text, nullable=True, comment="Formatted address of the property"
    )
    nombre_conjunto = Column(
        String(557), nullable=True, comment="Name of the residential complex"
    )
    prenbarrio = Column(String(40), nullable=True, comment="Neighborhood name")
    precbarrio = Column(String(6), nullable=True, comment="Neighborhood code")
    locnombre = Column(String(18), nullable=True, comment="Locality name")
    preusoph = Column(String(5), nullable=True, comment="Property use code")

    # Property characteristics
    esquinero = Column(
        Double,
        nullable=True,
        comment="Corner property indicator (1=corner, 0=not corner)",
    )
    viaprincipal = Column(
        Double, nullable=True, comment="Main road indicator (1=main road, 0=secondary)"
    )
    lista_precuso = Column(
        String(51), nullable=True, comment="List of property use codes"
    )
    lista_precdestin = Column(
        String(14), nullable=True, comment="List of property destination codes"
    )
    manzcodigo = Column(String(9), nullable=True, comment="Block code identifier")

    def __repr__(self):
        """String representation of the model."""
        return f"<BogotaDataCaracteristicas({self._format_attrs()})>"

    def _format_attrs(self):
        """Format all column attributes for string representation."""
        return ", ".join(
            f"{col.name}={getattr(self, col.name)}" for col in self.__table__.columns
        )
