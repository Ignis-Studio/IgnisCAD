class ICADError(Exception):
    """The base exception class of IgnisCAD"""
    pass


class InfeasibleEntityError(ICADError):
    """Raised when an entity is defined with infeasible arguments."""

    def __init__(self, entity, reason: str | list[str] | None = None):
        self.entity = entity
        self.label = getattr(self.entity, "name", None)
        if not self.label:
            self.label = str(self.entity)

        if isinstance(reason, str):
            self.reason = [reason]
        elif reason is None:
            self.reason = []
        else:
            self.reason = reason
        self.msg = f'The model "{self.label}" is physically infeasible.'
        if self.reason:
            self.msg += "\nReason:\n\t" + "\n\t".join(self.reason)
        super().__init__(self.msg)