class RepositoryError(Exception):
    pass


class EntityNotFoundError(RepositoryError):
    def __init__(self, entity_type: str, entity_id: str):
        super().__init__(f"Entity {entity_type} with id '{entity_id}' not found.")
