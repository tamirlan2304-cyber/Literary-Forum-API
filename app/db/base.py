from sqlalchemy.orm import DeclarativeBase, declared_attr

class Base(DeclarativeBase):

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"

from app.models.user import UserORM     # noqa: F401, E402
from app.models.post import PostORM      # noqa: F401, E402
from app.models.comment import CommentORM        # noqa: F401, E402
from app.models.tag import TagORM        # noqa: F401, E402
