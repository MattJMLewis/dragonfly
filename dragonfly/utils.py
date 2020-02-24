from config import URL


class Utils:

    @staticmethod
    def url(path):
        return f"{URL}/{path}"
