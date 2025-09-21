import redis.asyncio as aioredis
import src.config as config
JTI_EXPIRATION_TIME = 3600  # seconds

block_token_list = aioredis.from_url(
    config.Config.REDIS_URL,
)

async def add_jti_to_blocklist(jti: str) -> None:
    await block_token_list.set(
        name = "jti",
        value = "",
        ex = JTI_EXPIRATION_TIME
    )

async def token_in_blocklist(jti: str) -> bool:
    jti = await block_token_list.get("jti")
    return jti is not None