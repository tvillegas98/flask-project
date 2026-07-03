"""Capa de servicios: lógica de negocio de empleados.

Las rutas delegan aquí; este servicio orquesta reglas de negocio y delega la
persistencia en ``EmployeeRepository``.
"""

from __future__ import annotations

from repository import EmployeeRepository


class EmployeeService:
    """Casos de uso relacionados a empleados."""

    def __init__(self, repository: EmployeeRepository) -> None:
        self._repository = repository

    def create_employee(self, data: dict) -> dict:
        """Crea un empleado a partir de datos ya validados."""
        return self._repository.create(data)

    def get_employee(self, id: str) -> dict | None:
        """Recupera un empleado por id."""
        return self._repository.get_by_id(id)

    def list_employees(self, skip: int, limit: int) -> list[dict]:
        """Lista empleados paginados."""
        return self._repository.get_all(skip=skip, limit=limit)

    def update_employee(self, id: str, data: dict) -> dict | None:
        """Actualiza un empleado existente."""
        return self._repository.update(id, data)

    def delete_employee(self, id: str) -> bool:
        """Elimina un empleado."""
        return self._repository.delete(id)

    def average_salary(self) -> float:
        """Salario promedio de la empresa."""
        return self._repository.get_average_salary()
