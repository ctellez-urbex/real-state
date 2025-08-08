"""
Property Repository - Data Access Layer
Handles all database operations for property-related data.
"""
from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models import BogotaDataCaracteristicas, BogotaDataPredios


class PropertyRepository:
    """Repository pattern for property data access."""

    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)

    def get_properties_in_polygon(self, polygon: str) -> List[str]:
        """Get barmanpre codes within the specified polygon."""
        try:
            query = text(
                """
                SELECT barmanpre
                FROM bogota_data_lotes_fastsearch
                WHERE ST_CONTAINS(ST_GEOMFROMTEXT(:polygon, 4326), geometry)
            """
            )
            result = self.db.execute(query, {"polygon": polygon})
            rows = result.fetchall()
            if rows is None:
                return []
            return [row[0] for row in rows]
        except Exception as e:
            self.logger.error(f"Error getting properties in polygon: {e}")
            raise

    def get_property_characteristics(
        self, barmanpre_list: List[str]
    ) -> List[BogotaDataCaracteristicas]:
        """Get property characteristics for the given barmanpre list."""
        if not barmanpre_list:
            return []

        try:
            placeholders = ",".join(
                [":barmanpre_" + str(i) for i in range(len(barmanpre_list))]
            )
            query = text(
                f"""
                SELECT * FROM bogota_data_caracteristicas
                WHERE barmanpre IN ({placeholders})
            """
            )

            params = {
                f"barmanpre_{i}": barmanpre
                for i, barmanpre in enumerate(barmanpre_list)
            }
            result = self.db.execute(query, params)
            rows = result.fetchall()

            # Convert raw results to BogotaDataCaracteristicas objects
            characteristics = []
            if rows is None:
                return characteristics
            for row in rows:
                char_dict = dict(row._mapping)
                char = BogotaDataCaracteristicas(**char_dict)
                characteristics.append(char)

            return characteristics
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting property characteristics: {e}")
            raise

    def get_property_data(self, barmanpre_list: List[str]) -> List[BogotaDataPredios]:
        """Get property data for the given barmanpre list."""
        if not barmanpre_list:
            return []

        try:
            placeholders = ",".join(
                [":barmanpre_" + str(i) for i in range(len(barmanpre_list))]
            )
            query = text(
                f"""
                SELECT * FROM bogota_data_predios
                WHERE barmanpre IN ({placeholders})
            """
            )

            params = {
                f"barmanpre_{i}": barmanpre
                for i, barmanpre in enumerate(barmanpre_list)
            }
            result = self.db.execute(query, params)
            rows = result.fetchall()

            # Convert raw results to BogotaDataPredios objects
            property_data = []
            if rows is None:
                return property_data
            for row in rows:
                prop_dict = dict(row._mapping)
                prop = BogotaDataPredios(**prop_dict)
                property_data.append(prop)

            return property_data
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting property data: {e}")
            raise

    def get_property_geometry(self, barmanpre_list: List[str]) -> List[Dict[str, Any]]:
        """Get geometry data for properties."""
        try:
            if not barmanpre_list:
                return []

            placeholders = ",".join(
                [":barmanpre_" + str(i) for i in range(len(barmanpre_list))]
            )
            query = text(
                f"""
                SELECT barmanpre, ST_AsText(geometry) as wkt
                FROM bogota_data_lotes
                WHERE barmanpre IN ({placeholders})
            """
            )

            params = {
                f"barmanpre_{i}": barmanpre
                for i, barmanpre in enumerate(barmanpre_list)
            }
            result = self.db.execute(query, params)
            rows = result.fetchall()
            if rows is None:
                return []
            return [{"barmanpre": row[0], "wkt": row[1]} for row in rows]
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching geometry: {e}")
            raise
