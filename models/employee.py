from datetime import date

from marshmallow import Schema, fields, validate

def serialize_doc(doc: dict | None) -> dict | None:
    """Convierte un documento de Mongo en un dict serializable.

    Renombra `_id` (ObjectId) a `id` (str). Retorna ``None`` si el documento
    es ``None`` (por ejemplo, cuando no se encontró el registro).
    """
    if doc is None:
        return None

    serialized = dict(doc)
    if "_id" in serialized:
        serialized["id"] = str(serialized.pop("_id"))
    return serialized


class EmployeeSchema(Schema):
    """Esquema de un empleado de PeopleFlow."""

    id = fields.Str(dump_only=True)
    nombre = fields.Str(required=True)
    apellido = fields.Str(required=True)
    email = fields.Email(required=True)
    puesto = fields.Str(required=True)
    salario = fields.Float(
        required=True,
        validate=validate.Range(min=0, min_inclusive=False),
    )
    fecha_ingreso = fields.Date(load_default=date.today)


# Instancias reutilizables.
employee_schema = EmployeeSchema()
employee_schema_partial = EmployeeSchema(partial=True)
