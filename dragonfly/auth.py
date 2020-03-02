from datetime import datetime, timedelta

from dragonfly.request import request
from models.session import Session
from models.user import User


class Auth:
    """Provides a way to interact with the currently authenticated user."""

    @staticmethod
    def user():
        """
        Get the currently logged in user using the ``session_id`` stored in the cookies. It should be very unlikely that two
        sessions with the same ID exist

        :return: The currently logged in user.
        :type: :class:`User`
        """
        session_id = request.cookies['session_id']
        user = User().where('session_id', '=', session_id).first()
        return user

    @staticmethod
    def get(key, model=False):
        """
        Retrieve any keys stored in the ``Sessions`` table associated with the current ``session_id``

        :param key: The key of the value to retrieve
        :type: str

        :param model: If the entire model should be returned or the individual key value pair
        :type: bool

        :return: The model or value
        """
        session = Session().multiple_where({'name': key, 'session_id': request.cookies['session_id']}).first()

        if not session:
            return None

        if model:
            return session

        return session.value

    @staticmethod
    def set(key, value, force=False):
        """
        Set a key value pair in the ``Sessions`` table

        :param key: The key
        :type: str
        :param value: The value

        :param force: If the sessions table should be forced to update the value
        :type: bool
        """
        session = Auth.get(key, True)

        # Create a new session if it does not exist
        if not session:
            Session().create({'name': key, 'value': value, 'session_id': request.cookies['session_id']})
        elif force is True:
            session.update({'value': value})
        else:
            # If our session has not been updated for 12 hrs then we will force an update. This
            # ensures any data is new. Mainly used to ensure 'csrf_token' is up to date
            if datetime.now() - timedelta(hours=12) > session.updated_at:
                session.update({'value': value})
