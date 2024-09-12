from core.mongodb import Manager
from core.exceptions import AuthenticationFailedError

from .utils import collection, OAuth2Scheme, verified_access_token


async def get_user(token: OAuth2Scheme) -> dict:
    return await Manager.get_or_fail(
        collection,
        verified_access_token(token),
        AuthenticationFailedError
    )
