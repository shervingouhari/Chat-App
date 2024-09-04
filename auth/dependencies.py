from pydantic import ValidationError
import jwt

from core.settings import JWT_SECRET_KEY, JWT_ALGORITHM
from core.database_utils import get_or_fail
from core.exceptions import AuthenticationFailedError
from .schemas import TokenPayload
from .utils import collection, OAuth2Scheme, MongoDB


async def get_user(token: OAuth2Scheme, db: MongoDB):
    try:
        token = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM], verify=True)
    except jwt.InvalidTokenError:
        raise AuthenticationFailedError

    try:
        res = TokenPayload(username=token.get("username"), email=token.get("email"))
    except ValidationError:
        raise AuthenticationFailedError

    return await get_or_fail(collection, res.model_dump(), db, AuthenticationFailedError)
