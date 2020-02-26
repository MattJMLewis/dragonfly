from config import URL


class Utils:

    @staticmethod
    def url(path):
        """
        Generate a URL for a specific route
        :param path: The path of the URL
        :return: The generated URL
        """
        return f"{URL}/{path}"
