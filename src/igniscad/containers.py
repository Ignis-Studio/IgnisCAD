"""
Containers which implied session(*with* statements) functions.
Every container is a context manager.
"""
from igniscad.core import Entity

class Model(Entity):
    """
    A context manager to capture generated models(Entity objects).
    """

    def __init__(self, name):
        super().__init__(part=None, name=name)
        self.registry = {}

    # Context manager for *with* statements.
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.part:
            self.part.label = self.name  # names as labels
        return

    # Operator overriding
    def __lshift__(self, other):
        """
        Override the "<<" operator
        Usage: model << Entity(...)
        """
        if isinstance(other, Entity):
            self.part = self.part + other.part if self.part else other.part
            if other.name:
                self.registry[other.name] = other
        return self

    # Registry utils

    # Note: advantages of using a registry:
    # being *disvariabled*
    # you can define an entity without wrapping them into a variable
    # variables are easy to be ripped off between different contexts
    # you can call this entity anywhere through model.f(<entity.name_in_registry>)
    # you can also edit the registry by yourself, but that's not recommended.
    def find(self, name: str):
        """
        To find an Entity by its name in the registry.
        Args:
            name (str): Entity name
        """
        if name in self.registry:
            return self.registry[name]
        raise ValueError(f"❌ Part '{name}' not found in this model.")

    def f(self, name: str):
        return self.find(name)

class Group(Entity):
    """
    Combine multiple entities into a single Group Entity.
    Support the same context-manager syntax (as Model does).
    Entities within a group are automatically unioned.
    The Group object can be moved or aligned like a normal Entity outside the *with* statements.
    """

    def __init__(self, name=None):
        """
        Args:
            name: name of the Group in context registry
        """
        super().__init__(part=None, name=name)
        # Calling transforming functions right after initialization may cause an AttributeError
        # That is WAI.

    # Context manager for *with* statements.
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    def __lshift__(self, other):
        """
        Override the "<<" operator
        Usage: group << Entity(...)

        Every entity added is unioned automatically.
        """
        if isinstance(other, Entity):
            if self.part is None:
                # Initialize a new group with the current part as a basement.
                self.part = other.part
            else:
                # Union the new part with the old parts.
                self.part += other.part
        else:
            raise ValueError("❌ Group implies adding Entity objects (Box, Cylinder, etc.)")

        return self