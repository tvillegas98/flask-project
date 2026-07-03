import os

from dotenv import load_dotenv
from flask import Flask
from pymongo import MongoClient

def build_mongo_uri() -> str:
    """
    Arma la URI de conexión a MongoDB desde variables de entorno.
    """

    user = os.environ["MONGO_USER"]
    password = os.environ["MONGO_PASSWORD"]
    host = os.environ.get("MONGO_HOST", "localhost")
    port = os.environ.get("MONGO_PORT", "27017")
    return f"mongodb://{user}:{password}@{host}:{port}/"


def create_app() -> Flask:
    """
    Crea y configura la aplicación Flask.
    """
    mongo_uri = build_mongo_uri()
    db_name = os.environ["DB_NAME"]

    app = Flask(__name__)

    client = MongoClient(mongo_uri)
    collection = client[db_name]["employees"]

    collection.create_index("email", unique=True)

    app.extensions["mongo_client"] = client

    return app


if __name__ == "__main__":
    load_dotenv()
    app = create_app()
    host = os.environ.get("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_RUN_PORT", "5000"))
    app.run(host=host, port=port)
