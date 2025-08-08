"""
Bogotá real estate database models.

This module contains SQLAlchemy models for the existing Bogotá real estate database tables.
"""

# All implemented models connected to the real database
from .data_andenes import BogotaDataAndenes
from .data_barrio_catastral import BogotaDataBarrioCatastral
from .data_calzada import BogotaDataCalzada
from .data_caracteristicas import BogotaDataCaracteristicas
from .data_construcciones import BogotaDataConstrucciones
from .data_ejevial_paso import BogotaDataEjevialPaso
from .data_listings_activos import DataListingsActivos
from .data_localidad import BogotaDataLocalidad
from .data_lotes import BogotaDataLotes
from .data_lotes_fastsearch import BogotaDataLotesFastsearch
from .data_predios import BogotaDataPredios
from .galeria_precios import BogotaGaleriaPrecios
from .grid_polygon import BogotaGridPolygon
from .lotes_normativa import BogotaLotesNormativa
from .lotes_normativa_dict import BogotaLotesNormativaDict

__all__ = [
    # Infrastructure and urban data
    "BogotaDataAndenes",
    "BogotaDataBarrioCatastral",
    "BogotaDataCalzada",
    "BogotaDataEjevialPaso",
    "BogotaDataLocalidad",
    "BogotaGridPolygon",
    # Property and lot data
    "BogotaDataCaracteristicas",
    "BogotaDataConstrucciones",
    "BogotaDataLotes",
    "BogotaDataLotesFastsearch",
    "BogotaDataPredios",
    # Normative data
    "BogotaLotesNormativa",
    "BogotaLotesNormativaDict",
    # Market data
    "BogotaGaleriaPrecios",
    "DataListingsActivos",
]
