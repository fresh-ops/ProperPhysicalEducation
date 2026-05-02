from domain.ports.errors import RepositoryError


class JsonRepositoryError(RepositoryError):
    pass


class InvalidDirectoryError(JsonRepositoryError):
    def __init__(self, path: str):
        super().__init__(f"'{path}' is not a valid directory.")


class JsonReadError(JsonRepositoryError):
    def __init__(self, file_path: str, original_exception: Exception):
        super().__init__(f"Error reading JSON file '{file_path}': {original_exception}")


class JsonParseError(JsonRepositoryError):
    def __init__(self, file_path: str, original_exception: Exception):
        super().__init__(f"Error parsing JSON file '{file_path}': {original_exception}")
