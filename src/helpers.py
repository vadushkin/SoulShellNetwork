from src.questions.models import Question, Answer
from src.users.models import User


def update_votes(obj: Question | Answer, user: User, value: str | bool) -> None:
    """Updates votes for either a question or answer"""

    obj.votes.update_or_create(
        user=user,
        defaults={"value": value},
    )
    obj.count_votes()
