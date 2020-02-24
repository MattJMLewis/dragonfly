from dragonfly.request import request
from models.user import User
from models.session import Session
from datetime import datetime, timedelta

class Auth:

    @staticmethod
    def user():
        session_id = request.cookies['session_id']
        user = User().where('session_id', '=', session_id).first()
        return user

    @staticmethod
    def get(key, model=False):
        session = Session().multiple_where({'name': key, 'session_id': request.cookies['session_id']}).first()

        if not session:
            return None

        if model:
            return session

        return session.value

    @staticmethod
    def set(key, value):

        session = Auth.get(key, True)

        if not session:
            Session().create({'name': key, 'value': value, 'session_id': request.cookies['session_id']})
        else:
            if datetime.now() - timedelta(hours=12) > session.updated_at:
                session.update({'value': value})
