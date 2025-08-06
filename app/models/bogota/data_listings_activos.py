"""
Model for data_listings_activos table.

This table contains active property listings with full details.
"""

from sqlalchemy import Column, Integer, String, Double, Text
from geoalchemy2 import Geometry
from app.models.base import Base


class DataListingsActivos(Base):
    """Model for data_listings_activos table."""
    
    __tablename__ = "data_listings_activos"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, comment="Primary key identifier")
    
    # Listing identification
    code = Column(String(15), nullable=True, comment="Listing code identifier")
    tipoinmueble = Column(String(11), nullable=True, comment="Property type (apartment, house, etc.)")
    tiponegocio = Column(String(8), nullable=True, comment="Business type (sale, rent, etc.)")
    
    # Property measurements
    areaconstruida = Column(Double, nullable=True, comment="Built area in square meters")
    habitaciones = Column(Double, nullable=True, comment="Number of bedrooms")
    banos = Column(Double, nullable=True, comment="Number of bathrooms")
    garajes = Column(Double, nullable=True, comment="Number of parking spaces")
    
    # Financial information
    valor = Column(Double, nullable=True, comment="Property value in local currency")
    valoradministracion = Column(Double, nullable=True, comment="Administration fee value")
    
    # Property details
    antiguedad = Column(String(8), nullable=True, comment="Property age")
    piso = Column(Double, nullable=True, comment="Floor number")
    estrato = Column(Double, nullable=True, comment="Socioeconomic stratum (1-6)")
    
    # Dates
    fecha_insertado = Column(Text, nullable=True, comment="Date when listing was inserted")
    fecha_inicial = Column(Text, nullable=True, comment="Initial listing date")
    
    # Contact information
    contacto = Column(String(62), nullable=True, comment="Contact person name")
    email = Column(String(93), nullable=True, comment="Contact email address")
    telefonos = Column(String(148), nullable=True, comment="Contact phone numbers")
    
    # Location
    direccion = Column(String(198), nullable=True, comment="Property address")
    dpto_ccdgo = Column(String(4), nullable=True, comment="Department code")
    dpto_cnmbr = Column(String(56), nullable=True, comment="Department name")
    mpio_ccdgo = Column(String(5), nullable=True, comment="Municipality code")
    mpio_cnmbr = Column(String(27), nullable=True, comment="Municipality name")
    coddir = Column(String(198), nullable=True, comment="Address code")
    latitud = Column(Double, nullable=True, comment="Latitude coordinate")
    longitud = Column(Double, nullable=True, comment="Longitude coordinate")
    
    # Market information
    valormt2 = Column(String(20), nullable=True, comment="Price per square meter")
    inmobiliaria = Column(String(73), nullable=True, comment="Real estate agency name")
    
    # Content and media
    url = Column(String(180), nullable=True, comment="Original listing URL")
    url_img = Column(Text, nullable=True, comment="Property images URLs")
    descripcion = Column(Text, nullable=True, comment="Property description")
    desc = Column(Text, nullable=True, comment="Additional description")
    
    # Geometry
    delgeometry = Column(Text, nullable=True, comment="Geometry description")
    geometry = Column(Geometry, nullable=True, comment="Spatial geometry of the property")
    
    def __repr__(self):
        """String representation of the model."""
        return f"<DataListingsActivos({self._format_attrs()})>"
    
    def _format_attrs(self):
        """Format all column attributes for string representation."""
        return ', '.join(f"{col.name}={getattr(self, col.name)}" 
                        for col in self.__table__.columns)
