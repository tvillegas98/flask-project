# PeopleFlow API

API REST en Flask + MongoDB para gestionar los empleados de la empresa **PeopleFlow**.

## Arquitectura

Se armó una arquitectura en capas, utilizando el Patrón Repository.  
El flujo de una request es la siguiente

```
routes.py  →  services.py  →  repository.py  →  MongoDB
 (API)         (negocio)       (acceso a datos)
```

## Modelo `Employee`

| Campo           | Tipo   | Reglas                                  |
| --------------- | ------ | --------------------------------------- |
| `id`            | str    | Solo lectura (ObjectId de Mongo)  |
| `nombre`        | str    | requerido                               |
| `apellido`      | str    | requerido                               |
| `email`         | str    | requerido, formato email, **único**     |
| `puesto`        | str    | requerido                               |
| `salario`       | float  | requerido, mayor a 0                     |
| `fecha_ingreso` | date   | opcional, default hoy                    |

La unicidad de `email` se garantiza a nivel base de datos con un índice único creado al iniciar la app.

## Configuración

Variables de entorno (ver [.env.example](.env.example)):

| Variable          | Descripción                                         |
| ----------------- | --------------------------------------------------- |
| `MONGO_USER`      | Usuario de MongoDB                                  |
| `MONGO_PASSWORD`  | Password de MongoDB                                 |
| `MONGO_HOST`      | Host de Mongo (`mongo` en Docker, `localhost` local)|
| `MONGO_PORT`      | Puerto de Mongo                                     |
| `DB_NAME`         | Nombre de la base de datos                          |
| `JWT_SECRET`      | Secreto para firmar los JWT (obligatoria)          |
| `JWT_EXP_MINUTES` | Minutos de validez del token (default 60)          |
| `AUTH_USERNAME`   | Usuario para `POST /auth/login` (default admin)    |
| `AUTH_PASSWORD`   | Password para `POST /auth/login` (default admin)   |

```bash
cp .env.example .env
```

## Setup con Docker

- Tener Docker instalado, ya sea en su versión desktop o engine.  
- Haber configurado las variables de entorno en .env

Ejecutar lo siguiente
```
make up 
```

También vale ejecutar `make up-d` para levantar el docker-compose en segundo plano.

Una vez hecho eso, verificar el funcionamiento de la API con Postman/Bruno.


## Setup Local

- Tener Docker instalado, ya sea en su versión desktop o engine.  
- Tener instalado Python 3.11+
- Crear un virtual environment `python3 -m venv .venv`
- Activar el entorno virtual `source .venv/bin/activate`
- Ejecutar `make db` para levantar la base de MongoDB
- Ejecutar `make run` para levantar la aplicación

## Ejemplos con curl

```bash
# Crear
curl -X POST http://localhost:5000/employees \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Ana","apellido":"Pérez","email":"ana@peopleflow.com","puesto":"Backend","salario":1200.5}'

# Listar (paginado)
curl "http://localhost:5000/employees?skip=0&limit=10"

# Obtener por id
curl http://localhost:5000/employees/<id>

# Actualizar (parcial)
curl -X PUT http://localhost:5000/employees/<id> \
  -H "Content-Type: application/json" \
  -d '{"salario":1500}'

# Eliminar
curl -X DELETE http://localhost:5000/employees/<id>

# Salario promedio
curl http://localhost:5000/reports/salary-average
```

## Autenticación

Todos los endpoints de empleados y el reporte requieren un **JWT** en el header `Authorization: Bearer <token>`. El token se obtiene en `POST /auth/login`

```bash
# 1. Login → token
TOKEN=$(curl -s -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' | jq -r .token)

# 2. Usar el token
curl http://localhost:5000/employees -H "Authorization: Bearer $TOKEN"
```

Sin token (o con uno inválido/expirado) los endpoints protegidos responden `401`.

## Endpoints

| Método | Ruta                      | Descripción                          | Códigos           |
| ------ | ------------------------- | ------------------------------------ | ----------------- |
| POST   | `/auth/login`             | Emite un JWT (público)               | 200 / 401         |
| POST   | `/employees`              | Crea un empleado                     | 201 / 400 / 401 / 409 |
| GET    | `/employees`             | Lista empleados (`?skip=&limit=`)    | 200 / 400 / 401   |
| GET    | `/employees/<id>`         | Obtiene un empleado                  | 200 / 400 / 401 / 404 |
| PUT    | `/employees/<id>`         | Actualiza (parcial) un empleado      | 200 / 400 / 401 / 404 / 409 |
| DELETE | `/employees/<id>`         | Elimina un empleado                  | 204 / 400 / 401 / 404 |
| GET    | `/reports/salary-average` | Salario promedio de la empresa       | 200 / 401         |

Notas:
- `400` — body inválido, `id` no es un ObjectId válido, o `skip`/`limit` no enteros.
- `401` — token JWT ausente, inválido o expirado (o credenciales inválidas en login).
- `409` — email duplicado (en la creación).
- `GET /employees` usa por defecto `skip=0` y `limit=20`.

## Colección Postman


En la carpeta [postman/PeopleFlow.postman_collection.json](postman/PeopleFlow.postman_collection.json) se incluyó una collección para poder verificar el funcionamiento de la API.


## Que falta

- Agregar tests unitarios