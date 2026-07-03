"""
El repositorio es el único responsable del mapeo entre documentos de MongoDB y
los dicts que usa el resto de la aplicación: en la escritura codifica los tipos
que Mongo necesita (p. ej. `date` -> `datetime`) y en la lectura devuelve dicts
serializables (`_id` -> `id` string, `datetime` -> `date`).
"""

from __future__ import annotations

from datetime import date, datetime

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.collection import Collection

from models.employee import serialize_doc


class EmployeeRepository:
    """Acceso a datos de empleados en MongoDB."""

    def __init__(self, collection: Collection) -> None:
        self._collection = collection

    def create(self, data: dict) -> dict:
        """Inserta un empleado y devuelve el documento creado (con id)."""
        doc = self._to_mongo(data)
        result = self._collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return self._from_mongo(doc)

    def get_by_id(self, id: str) -> dict | None:
        """Devuelve el empleado con el id dado, o ``None`` si no existe."""
        doc = self._collection.find_one({"_id": ObjectId(id)})
        return self._from_mongo(doc)

    def get_all(self, skip: int, limit: int) -> list[dict]:
        """Devuelve una página de empleados aplicando skip/limit."""
        cursor = self._collection.find().skip(skip).limit(limit)
        return [self._from_mongo(doc) for doc in cursor]

    def update(self, id: str, data: dict) -> dict | None:
        """Actualiza un empleado y devuelve el documento resultante, o ``None``."""
        if not data:
            return self.get_by_id(id)

        doc = self._collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": self._to_mongo(data)},
            return_document=ReturnDocument.AFTER,
        )
        return self._from_mongo(doc)

    def delete(self, id: str) -> bool:
        """Elimina un empleado; devuelve ``True`` si se borró algo."""
        result = self._collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

    def get_average_salary(self) -> float:
        """Devuelve el salario promedio de todos los empleados."""
        pipeline = [{"$group": {"_id": None, "average": {"$avg": "$salario"}}}]
        result = list(self._collection.aggregate(pipeline))
        return round(result[0]["average"], 2) if result else 0.0

    @staticmethod
    def _to_mongo(data: dict) -> dict:
        """Codifica un dict de la app para almacenarlo en Mongo."""
        doc = dict(data)
        fecha = doc.get("fecha_ingreso")
        # Mongo (BSON) no soporta `date`, solo `datetime`.
        if isinstance(fecha, date) and not isinstance(fecha, datetime):
            doc["fecha_ingreso"] = datetime(fecha.year, fecha.month, fecha.day)
        return doc

    @staticmethod
    def _from_mongo(doc: dict | None) -> dict | None:
        """Convierte un documento de Mongo en un dict serializable de la app."""
        serialized = serialize_doc(doc)
        if serialized is None:
            return None

        fecha = serialized.get("fecha_ingreso")
        if isinstance(fecha, datetime):
            serialized["fecha_ingreso"] = fecha.date()
        return serialized
