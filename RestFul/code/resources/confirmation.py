from time import time
from flask_restful import Resource
from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema
from libs.mailgun import MailGunException
from libs.strings import gettext

confirmation_schema = ConfirmationSchema()


class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": gettext("confirmation_not_found")}, 404
        if confirmation.expired:
            return {"message": gettext("confirmation_expired")}, 400
        if confirmation.confirmed:
            return {"message": gettext("confirmation_already_confirmed")}, 400
        
        confirmation.confirmed = True
        confirmation.save_to_db()
        return {"message": gettext("confirmation_user_confirmed")}, 200


class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("user_not_found")}, 404
        return(
            {
                "current_time": int(time()),
                "confirmation": [
                    confirmation_schema.dump(each)
                    for each in user.confirmation.order_by(ConfirmationModel.expire_at)
                ]
            }
        )
        
    @classmethod
    def post(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("user_not_found")}, 404
        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message": gettext("confirmation_already_confirmed")}, 400
                confirmation.force_to_expire()
            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db
            user.send_confirmation_email()
            return {"message": gettext("confirmation_resend_successfully")}, 201
        except MailGunException as e:
            return {"message": str(e)}, 500
        except:
            return {"message": gettext("confirmation_resend_fail")}, 500