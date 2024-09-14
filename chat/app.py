import json

from socketio.exceptions import ConnectionRefusedError
import socketio
import bson

from core import mongodb, redis
from core.exceptions import EntityDoesNotExistError, EntityAlreadyExistsError
from core.settings import SOCKETIO_PING_INTERVAL, SOCKETIO_PING_TIMEOUT, SOCKETIO_DEBUG, SOCKETIO_CORS_ALLOWED_ORIGINS
from auth.utils import verified_access_token
from .exceptions import (
    authentication_failed_error,
    entity_does_not_exist_error,
    entity_already_exists_error,
    receiver_required_error,
    sender_is_receiver_error
)


sio = socketio.AsyncServer(
    async_mode='asgi',
    ping_interval=SOCKETIO_PING_INTERVAL,
    ping_timeout=SOCKETIO_PING_TIMEOUT,
    logger=SOCKETIO_DEBUG,
    engineio_logger=SOCKETIO_DEBUG,
    cors_allowed_origins=SOCKETIO_CORS_ALLOWED_ORIGINS
)
# sio.instrument(auth={
#     'username': 'admin',
#     'password': "admin",
# })
server = socketio.ASGIApp(sio)


if SOCKETIO_DEBUG:
    from core.logging import log

    @sio.on('*')
    async def any_event(event, sid, data):
        log.info(f"{event=} | {sid=} | {data=}")


@sio.event
async def connect(sid, environ):
    token = environ.get("HTTP_AUTHORIZATION")
    if not token or not token.startswith("Bearer "):
        raise ConnectionRefusedError(authentication_failed_error)
    token = token.split(" ")[1]

    try:
        user = await mongodb.Manager.get_or_create(
            "users",
            verified_access_token(token)
        )
    except (EntityAlreadyExistsError):
        raise ConnectionRefusedError(entity_already_exists_error)

    await redis.Manager.get_db().set(
        sid,
        json.dumps(
            {
                "_id": str(user["_id"]),
                "username": user["username"]
            }
        ))


@sio.event
async def disconnect(sid):
    await redis.Manager.get_db().delete(sid)


@sio.event
async def private_room(sid, data):
    sender_id = json.loads(await redis.Manager.get_db().get(sid)["_id"])

    if (receiver_username := data.get("receiver")) is None:
        return await sio.emit(**receiver_required_error, to=sid)

    try:
        receiver = mongodb.Manager.get_or_fail(
            "users",
            {"username": receiver_username}
        )
    except EntityDoesNotExistError:
        return await sio.emit(**entity_does_not_exist_error, to=sid)
    receiver_id = str(receiver["_id"])

    if sender_id == receiver_id:
        return await sio.emit(**sender_is_receiver_error, to=sid)

    room = await mongodb.Manager.get_or_create("rooms", {
        "type": "private",
        "participants": sorted([sender_id, receiver_id])
    })

    await mongodb.Manager.get_db()["users"].update_one({"_id": sender_id}, {"$addToSet": {"rooms": room["_id"]}})
    await mongodb.Manager.get_db()["users"].update_one({"_id": receiver_id}, {"$addToSet": {"rooms": room["_id"]}})

    room_id = str(room["_id"])
    await sio.enter_room(sid, room_id)
    return room_id


@sio.event
async def private_message(sid, data):
    if (user := await redis.Manager.get_db().get(sid)) is None:
        return await sio.emit("error", "Authentication required.", to=sid)
    sender = json.loads(user)["username"]

    room = data.get("room")
    message = data.get("message")
    if room is None or message is None:
        return await sio.emit("error", "Room and message are required.", to=sid)

    try:
        room_id = bson.ObjectId(room)
    except bson.errors.InvalidId:
        return await sio.emit("error", "Invalid room object id.", to=sid)

    # return await Manager.get_db()["rooms"].update_one(
    #     {"_id": room_id},
    #     {"$push": {"messages": {
    #         "sender": sender,
    #         "message": message,
    #         "timestamp": dt.datetime.now(dt.timezone.utc)
    #     }}}
    # )

    res = await add_message_to_room(mongodb.Manager.get_db(), room_id, sender, message)
    if res.matched_count != 1:
        return await sio.emit("error", "Room does not exist.", to=sid)

    await sio.emit("private_message", data=message, room=room)


@sio.event
async def previous_rooms(sid, _):
    if (user := await redis.Manager.get_db().get(sid)) is None:
        return await sio.emit("error", "User is not authenticated.", to=sid)

    _id = bson.ObjectId(json.loads(user)["_id"])
    mdb = mongodb.Manager.get_db()

    if (user := await mdb["users"].find_one({"_id": _id})) is None:
        return await sio.emit("error", "User does not exist.", to=sid)

    if (rooms := user.get("rooms")) is None:
        return []

    rooms = await mdb["rooms"].find({"_id": {"$in": rooms}}).to_list(length=None)
    return [room["type"] for room in rooms]
