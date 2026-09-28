from app.repositories import BaseRepository
from app.models.post import Post


class PostRepository(BaseRepository[Post]):
    def __init__(self):
        super().__init__(Post)


post_repository = PostRepository()
