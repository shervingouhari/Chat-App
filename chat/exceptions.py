authentication_failed_error = {
    "event": "error",
    "data": {
        "detail": {
            "type": "AuthenticationFailedError",
            "message": "Authentication failed.",
            "resolution": "Please ensure your token is valid and connect again.",
        }
    }
}

entity_does_not_exist_error = {
    "event": "error",
    "data": {
        "detail": {
            "type": "EntityDoesNotExistError",
            "message": "Receiver does not exist in the database.",
            "resolution": "Ensure the given username is correct, and the entity exists."
        }
    }
}

entity_already_exists_error = {
    "event": "error",
    "data": {
        "detail": {
            "type": "EntityAlreadyExistsError",
            "message": "Conflict detected.",
            "resolution": "Please ensure your token is valid and connect again.",
        }
    }
}

receiver_required_error = {
    "event": "error",
    "data": {
        "detail": {
            "type": "ReceiverRequiredError",
            "message": "Receiver is required.",
            "resolution": "Please ensure you include the receiver username.",
        }
    }
}

sender_is_receiver_error = {
    "event": "error",
    "data": {
        "detail": {
            "type": "SenderIsReceiverError",
            "message": "You cannot create a private room with yourself.",
            "resolution": "Please select a different user to chat with."
        }
    }
}
