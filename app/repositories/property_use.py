"""
Property Use Repository - Handles property use classifications and mappings.
"""
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.core.logging import get_logger


class PropertyUseRepository:
    """Repository for property use classifications and mappings."""

    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)

    def get_property_use_codes_by_type(self, property_types: List[str]) -> List[str]:
        """
        Get property use codes based on property types.

        Args:
            property_types: List of property type classifications

        Returns:
            List of precuso codes that match the property types
        """
        if not property_types:
            return []

        try:
            # Check if 'todo' is in the list (include all)
            if any(isinstance(x, str) and "todo" in x.lower() for x in property_types):
                return []  # Return empty to include all

            # This would typically query a classification table
            # For now, we'll implement a basic mapping
            property_type_mapping = {
                "residencial": ["01", "02", "03"],
                "comercial": ["04", "05", "06"],
                "industrial": ["07", "08", "09"],
                "institucional": ["10", "11", "12"],
                "recreativo": ["13", "14", "15"],
            }

            codes = []
            for prop_type in property_types:
                if isinstance(prop_type, str):
                    prop_type_lower = prop_type.lower()
                    if prop_type_lower in property_type_mapping:
                        codes.extend(property_type_mapping[prop_type_lower])

            return list(set(codes))  # Remove duplicates

        except Exception as e:
            self.logger.error(f"Error getting property use codes: {e}")
            return []

    def get_property_use_classification(self) -> Dict[str, Any]:
        """
        Get the complete property use classification table.
        This would replace the usosuelo_class() function from the original code.
        """
        try:
            # This would query a classification table in the database
            # For now, return a basic structure
            return {
                "clasificacion": ["residencial", "comercial", "industrial"],
                "precuso": ["01", "02", "03", "04", "05", "06", "07", "08", "09"],
            }
        except Exception as e:
            self.logger.error(f"Error getting property use classification: {e}")
            return {}
