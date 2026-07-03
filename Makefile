COMPOSE := docker compose

.DEFAULT_GOAL := help
.PHONY: help up up-d down db db-down logs ps run install clean

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

up: ## Levanta todo el proyecto (API + Mongo) en Docker
	$(COMPOSE) up --build

up-d: ## Igual que `up` pero en segundo plano
	$(COMPOSE) up --build -d

down: ## Baja todos los contenedores
	$(COMPOSE) down

db: ## Levanta solo MongoDB
	$(COMPOSE) up -d mongo

db-down: ## Detiene solo MongoDB
	$(COMPOSE) stop mongo

logs: ## Sigue los logs de todos los servicios
	$(COMPOSE) logs -f

ps: ## Muestra el estado de los contenedores
	$(COMPOSE) ps

run: ## Corre la API en local (requiere `make db` corriendo; usa Mongo en localhost)
	MONGO_HOST=localhost FLASK_APP=app.py flask run

install: ## Instala las dependencias en el entorno actual
	pip install -r requirements.txt

clean: ## Baja los contenedores y borra el volumen de datos de Mongo
	$(COMPOSE) down -v
