from bson import ObjectId
from flask import Blueprint, abort, current_app, jsonify, request
from marshmallow import ValidationError
from pymongo.errors import DuplicateKeyError

from auth import jwt_required
from models import employee_schema, employee_schema_partial
from services import EmployeeService

employees_bp = Blueprint("employees", __name__)


def _service() -> EmployeeService:
    """Recupera el servicio de empleados desde el contexto de la app."""
    return current_app.extensions["employee_service"]


def _validate_object_id(id: str) -> None:
    """Aborta con 400 si el id no es un ObjectId de Mongo válido."""
    if not ObjectId.is_valid(id):
        abort(400, description="El id proporcionado no es un ObjectId válido.")


@employees_bp.post("/employees")
@jwt_required
def create_employee():
    try:
        data = employee_schema.load(request.get_json())
        created = _service().create_employee(data)
    except ValidationError as err:
        abort(400, description=err.messages)
    except DuplicateKeyError:
        abort(409, description="Ya existe un empleado con ese email.")

    return jsonify(employee_schema.dump(created)), 201


@employees_bp.get("/employees")
@jwt_required
def list_employees():
    try:
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 20))
    except (TypeError, ValueError):
        abort(400, description="skip y limit deben ser enteros.")

    employees = _service().list_employees(skip=skip, limit=limit)
    result = [employee_schema.dump(doc) for doc in employees]
    return jsonify(result), 200


@employees_bp.get("/employees/<id>")
@jwt_required
def get_employee(id: str):
    _validate_object_id(id)

    employee = _service().get_employee(id)
    if employee is None:
        abort(404, description="Empleado no encontrado.")

    return jsonify(employee_schema.dump(employee)), 200


@employees_bp.put("/employees/<id>")
@jwt_required
def update_employee(id: str):
    _validate_object_id(id)

    try:
        data = employee_schema_partial.load(request.get_json() or {})
        updated = _service().update_employee(id, data)
    except ValidationError as err:
        abort(400, description=err.messages)
    except DuplicateKeyError:
        abort(409, description="Ya existe un empleado con ese email.")

    if updated is None:
        abort(404, description="Empleado no encontrado.")

    return jsonify(employee_schema.dump(updated)), 200


@employees_bp.delete("/employees/<id>")
@jwt_required
def delete_employee(id: str):
    _validate_object_id(id)

    if not _service().delete_employee(id):
        abort(404, description="Empleado no encontrado.")

    return "", 204


@employees_bp.get("/reports/salary-average")
@jwt_required
def salary_average():
    average = _service().average_salary()
    return jsonify({"salary_average": average}), 200
