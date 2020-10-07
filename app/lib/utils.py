import logging
from app.extensions import db

from app.models import Message
from telegram.error import BadRequest


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)

logger = logging.getLogger("cleanup_worker.utils")

def cleanup_message(bot, _id, chat_id, message_id):
    """ Cleanup a single message from the Telegram api and the db """
    must_delete = False
    try:
        must_delete = bot.delete_message(chat_id=chat_id, message_id=message_id)
    # Skip if the message not found for any reason
    except BadRequest as e:
        logger.debug(
                f"While deleting a bot message: {e}"
        )
        must_delete = True
    except Exception as e:
        logger.debug(
                f"While deleting a bot message, chat_id={m.chat_id} , message_id={m.message_id}: {e}"
        )
        return 0
    if must_delete:
        db.session.query(Message).filter_by(id=_id).delete()
        db.session.commit()
        return 1
    return 0

def cleanup_all_user_messages(bot, chat_id, user_id):
    """ Cleanup all of the user messages from the Telegram api and the db """
    messages = db.session.query(Message).filter(
            user_id==user_id
    ).all()
    logger.info(
            f"Start to cleaning up {len(messages)} message for user_id({user_id})..."
    )
    
    deleted = 0
    for m in messages:
        deleted += cleanup_message(bot, m.id, m.chat_id, m.message_id)

    logger.info(
            f"Cleaning up {deleted} message done for user_id({user_id})."
    )

