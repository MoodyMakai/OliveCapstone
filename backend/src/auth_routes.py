from functools import wraps

import aiosqlite
from quart import g, jsonify, request

from src.app import app
from src.database_helpers import hash_token


def require_auth(f):

    @wraps(f)
    async def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401

        raw_token = auth_header.split(" ")[1]
        token_hash = hash_token(raw_token)

        user = await app.storage.get_user(token=token_hash)

        if not user:
            return jsonify({"error": "Invalid token or session expired"}), 401
        if user.banned:
            return jsonify({"error": "Account is banned"}), 403
        if user.verified == 0:
            return jsonify({"error": "Email not verified"}), 403

        await app.storage.db.reset_token_lifetime(token_hash)

        return await f(*args, **kwargs)

    return decorated
