from quart import Blueprint, jsonify, request

from .tokens import verify_verification_token

# Blueprint name is Verify.sould
verification_bp = Blueprint("verify", __name__)


@verification_bp.route("/verify-email", methods=["GET"])
async def verify_user_email():
    # Import now not at start to prevent circular importing
    from src.app import app

    # Request gets url chooses the token argument.
    token = request.args.get("token")
    if not token:  # Returns Json and error 400 for Http
        return jsonify({"error": "failed to validate, missing token."}), 400

    # Verify the token 404 is not found
    email = verify_verification_token(token)
    if not email:
        return jsonify({"error": "token has expired or is invalid"}), 404

    # Get the User row from the database 
    ##Replace dont use app.db use app.storage
    user_info = await app.storage.get_user_by_email(email)
    if not user_info:
        return jsonify({"error": "user not found"}), 404
    # Gets specific field of row.
    verified = user_info.verified
    user_identifier = user_info.user_id
    # Error code 200 is completed / success
    if verified:
        return jsonify({"message": "email already verified."}), 200
    # Update the correct user verification to True
    await app.db.update_user_verification(user_identifier, True)
    return jsonify({"message": "email has been successfully verified"}), 200
