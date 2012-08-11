from abc import ABCMeta

class Uploader:
    __metaclass__ = ABCMeta

    @abstractmethod
    def upload_data(data):
        return None

    @abstractmethod
    def retrieve_data(identifier):
        return None

