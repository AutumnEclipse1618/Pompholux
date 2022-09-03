from app import app
from db.models.types import from_dict, MongoProjection
from db.models import Server


async def find_one(id_: int, projection: MongoProjection = None) -> Server:
    return from_dict(Server, await app.db_client.pompholux.servers.find_one({ "_id": id_ }, projection))
