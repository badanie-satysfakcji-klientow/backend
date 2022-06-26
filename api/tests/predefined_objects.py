from random import randint

from api.models import Creator, Survey, Item, Option, Question, Answer, Submission, Interviewee
from lorem_text import lorem


class Predefined:
    @staticmethod
    def create_creator():
        return Creator.objects.create(
            email=lorem.words(1) + '@test.com',
            password=lorem.words(1).replace(' ', '')
        )

    @staticmethod
    def create_survey(creator: Creator):
        return Survey.objects.create(
            title=lorem.words(5),
            description=lorem.sentence(),
            creator_id=creator,
            starts_at='2022-06-02T04:20:00Z',
            expires_at='2023-06-22T02:26:22Z',
            paused=False,
            anonymous=False,
            greeting=lorem.words(2),
        )

    @staticmethod
    def create_item(survey: Survey):
        return Item.objects.create(
            type=randint(1, 11),
            required=randint(0, 1) == 1,
            survey=survey,
        )

    @staticmethod
    def create_items(survey: Survey, count: int = 1):
        return [Predefined.create_item(survey) for _ in range(count)]

    @staticmethod
    def create_questions(item: Item, count: int = 1, start_index: int = 1):
        questions = []
        for _ in range(count):
            questions.append(Question.objects.create(
                order=_ + start_index,
                item=item,
                value=lorem.words(5),
            ))
        return questions

    @staticmethod
    def create_options(item: Item, count: int = 1):
        return [Option.objects.create(
            content=lorem.words(5),
            item=item
        ) for _ in range(count)]

    @staticmethod
    def create_submission(survey: Survey, interviewee: Interviewee):
        return Submission.objects.create(
            survey=survey,
            interviewee=interviewee
        )

    @staticmethod
    def create_interviewee():
        return Interviewee.objects.create(
            email=f'{lorem.words(1)}@{lorem.words(1)}.{lorem.words(1)}',
            first_name=lorem.words(1),
            last_name=lorem.words(1)
        )

    @staticmethod
    def create_answers(question: Question, submission: Submission, count: int = 1):
        return [Answer.objects.create(
            question=question,
            submission=submission,
            content_character=None,
            content_numeric=None,
            option=None
        ) for _ in range(count)]