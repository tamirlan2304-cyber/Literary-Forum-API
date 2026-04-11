from sqlalchemy.orm import DeclarativeBase, declared_attr

class Base(DeclarativeBase):

    @declared_attr.directive
    def __tablename__(cls) -> str:
        name = cls.__name__.replace("ORM", "").lower()
        return name + "s"



