class NotFoundException(Exception):
    def __init__(self, message: str = "Resource not found"):
        self.message = message
        super().__init__(self.message)


class BadRequestException(Exception):
    def __init__(self, message: str = "Bad request"):
        self.message = message
        super().__init__(self.message)
