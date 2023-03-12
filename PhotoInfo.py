
class PhotoInfo:
    # Some attributes
    __filename = ""
    __has_marker = False

    def __init__(self, filename, has_marker):
        self.__filename = filename
        self.__has_marker = has_marker

    def get_filename(self):
        return self.__filename

    def get_has_marker(self):
        return self.__has_marker
