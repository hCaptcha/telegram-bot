from flask import Blueprint, render_template, request, current_app
import urllib.request
import urllib.parse
import json

from app.config import get_active_config


blueprint = Blueprint("captcha", __name__, static_folder="../static")


@blueprint.route("/")
def index():
    return render_template("index.html")


@blueprint.route("/<chat_id>/<user_id>/<user_name>")
def captcha(chat_id=None, user_id=None, user_name=None):
    """
    This is responsible for showing the captcha.
    It takes an optional `callback_chat_id` param. This param is passed to the `verify` function below.
    """

    callback_chat_id = request.args.get("callback_chat_id", None)

    return render_template(
        "captcha.html",
        chat_id=chat_id,
        user_id=user_id,
        user_name=user_name,
        callback_chat_id=callback_chat_id,
        site_key=get_active_config().HCAPTCHA_SITE_KEY,
    )


@blueprint.route("/<chat_id>/<user_id>/<user_name>/verify", methods=["POST"])
def verify(chat_id=None, user_id=None, user_name=None):
    """
    This is responsible for verifying the captcha results (either pass or failure).
    It takes an optional `callback_chat_id` param. This param is passed to `HCaptchaBot.verify`.
    """

    callback_chat_id = request.args.get("callback_chat_id", None)

    token = request.form["h-captcha-response"]
    params = urllib.parse.urlencode(
        {"secret": get_active_config().HCAPTCHA_SECRET, "response": token}
    )

    with urllib.request.urlopen(
        get_active_config().HCAPTCHA_POST_URI, params.encode("ascii")
    ) as response:
        json_response = json.loads(response.read().decode("utf-8"))

        if json_response["success"]:
            current_app.logger.info(f"user_id: {user_id} solved captcha")

            current_app.bot_instance.verify(
                chat_id, user_id, user_name, callback_chat_id
            )

            return render_template("success.html")
        else:
            current_app.logger.info(f"user_id: {user_id} failed captcha")

            return render_template("error.html")
