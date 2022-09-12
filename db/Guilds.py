from app import app
from core.util import Int, uint64_to_int
from db.models.types import MongoProjection, from_dict, asdict
from db.models.Guild import Guild, Autochannel


async def find(id_: Int, projection: MongoProjection = None) -> Guild:
    return from_dict(Guild, await app.db_client.pompholux.guilds.find_one({"_id": uint64_to_int(id_)}, projection))


async def update_autochannel(id_: Int, autochannel: Autochannel):
    await app.db_client.pompholux.guilds.update_one(
        {"_id": uint64_to_int(id_)},
        { "$set": { "autochannel": asdict(autochannel) } }
    )


async def enable_autochannel(id_: Int, enabled: bool):
    await app.db_client.pompholux.guilds.update_one(
        {"_id": uint64_to_int(id_)},
        { "$set": { "autochannel.enabled": enabled } }
    )
