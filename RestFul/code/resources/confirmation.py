from time import time
from flask_restful import Resource
from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema
from resources.user import USER_NOT_FOUND
from libs.mailgun import MailGunException

NOT_FOUND = "Confirmation not found."
USER_CONFIRMED = "User confirmed."
ALREADY_CONFIRMED = "Registration has already been confirmed."
EXPIRED = "The link has expired"
RESEND_FAIL = "Internal server error, failed to resend confirmation email."
RESEND_SUCESSFULLY = "E-mail confirmation successfully re-sent."

confirmation_schema = ConfirmationSchema()

class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": NOT_FOUND}, 404
        if confirmation.expired:
            return {"message": EXPIRED}, 400
        if confirmation.confirmed:
            return {"message": ALREADY_CONFIRMED}, 400
        
        confirmation.confirmed = True
        confirmation.save_to_db()
        return {"message": USER_CONFIRMED}, 200
        
        

class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
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
            return {"message": USER_NOT_FOUND}, 404
        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message": ALREADY_CONFIRMED}, 400
                confirmation.force_to_expire()
            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db
            user.send_confirmation_email()
            return {"message": RESEND_SUCESSFULLY}, 201
        except MailGunException as e:
            return {"message": str(e)}, 500
        except:
            return {"message": RESEND_FAIL}, 500