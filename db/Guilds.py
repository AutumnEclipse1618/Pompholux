from app import app
from db.models.types import from_dict, MongoProjection
from db.models import Guild


async def find_one(id_: int, projection: MongoProjection = None) -> Guild:
    return from_dict(Guild, await app.db_client.pompholux.servers.find_one({"_id": id_}, projection))
