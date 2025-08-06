"""
Database models for the Real Estate API.

This module contains all SQLAlchemy models for the real estate application.
"""

from .base import Base
from .bogota import (
    # Infrastructure and urban data
    BogotaDataAndenes,
    BogotaDataBarrioCatastral,
    BogotaDataCalzada,
    BogotaDataEjevialPaso,
    BogotaDataLocalidad,
    BogotaGridPolygon,
    
    # Property and lot data
    BogotaDataCaracteristicas,
    BogotaDataConstrucciones,
    BogotaDataLotes,
    BogotaDataLotesFastsearch,
    BogotaDataPredios,
    
    # Normative data
    BogotaLotesNormativa,
    BogotaLotesNormativaDict,
    
    # Market data
    BogotaGaleriaPrecios,
    DataListingsActivos,
)

__all__ = [
    "Base",
    
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