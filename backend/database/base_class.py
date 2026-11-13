from sqlalchemy.orm import declarative_base, declared_attr

class CustomBase:
    """Base class for all SQLAlchemy declarative models."""

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

Base = declarative_base(cls=CustomBase)
