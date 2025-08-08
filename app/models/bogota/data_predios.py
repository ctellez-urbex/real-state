"""
Model for bogota_data_predios table.

This table contains property information and details for Bogotá.
"""

from sqlalchemy import Column, Double, Integer, String

from app.models.base import Base


class BogotaDataPredios(Base):
    """Model for bogota_data_predios table."""

    __tablename__ = "bogota_data_predios"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, comment="Primary key identifier")

    # Property identification
    barmanpre = Column(
        String(25), nullable=True, comment="Barmanpre code - unique property identifier"
    )
    prechip = Column(
        String(25),
        nullable=True,
        comment="Property CHIP (Catastral Homologation and Identification of Properties)",
    )

    # Location information
    prenbarrio = Column(String(40), nullable=True, comment="Property neighborhood name")
    precbarrio = Column(String(6), nullable=True, comment="Property neighborhood code")

    # Area measurements
    preaconst = Column(
        Double, nullable=True, comment="Construction area in square meters"
    )
    preaterre = Column(Double, nullable=True, comment="Land area in square meters")
    prevetustz = Column(Double, nullable=True, comment="Property age in years")

    # Cadastral information
    precedcata = Column(String(20), nullable=True, comment="Cadastral record code")
    predirecc = Column(String(60), nullable=True, comment="Property address")
    precuso = Column(String(4), nullable=True, comment="Property use code")
    precdestin = Column(String(3), nullable=True, comment="Property destination code")
    preusoph = Column(String(4), nullable=True, comment="Property use code for PH")
    matriculainmobiliaria = Column(
        String(13), nullable=True, comment="Real estate registration number"
    )

    # Socioeconomic data
    estrato = Column(Double, nullable=True, comment="Socioeconomic stratum (1-6)")

    def __repr__(self):
        """String representation of the model."""
        return f"<BogotaDataPredios({self._format_attrs()})>"

    def _format_attrs(self):
        """Format all column attributes for string representation."""
        return ", ".join(
            f"{col.name}={getattr(self, col.name)}" for col in self.__table__.columns
        )
