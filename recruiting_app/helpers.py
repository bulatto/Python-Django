from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse

from recruiting.settings import EMAIL_HOST_USER
from recruiting_app.models import Test, Result, Sith, Recruit


simple_html_text = (
    "<h2 style='text-align: center;'>{0}<h2><p>"
    "<a style='display: block;text-align:center;'"
    " href='/'>Перейти на главную страницу</a></p>"
)


# Отправка почтового сообщения от ситха рекруту
def send_email_to_recruit(sith, recr):
    mail_count = send_mail(
        'Ты был выбран Рукой Тени!',
        'Поздравляю, {0}! Ты был выбран Рукой Тени для ситха "{1}" (id={2})'.format(
            recr.name, sith.name, sith.id),
        EMAIL_HOST_USER,
        [recr.email],
        fail_silently=True
    )
    return bool(mail_count)


@transaction.atomic
def calculate_test_results(recruit, post_dict):
    """Записывает результаты тестов рекрута в бд и подсчитывает количество
    правильных ответов
    """
    count = 0
    for question in Test.objects.all().order_by('id').iterator():
        answer = post_dict.get("question{0}".format(question.id))
        answer = True if answer == "True" else False  # Перевод в bool
        Result.objects.create(
            recruit=recruit, question=question, answerOfRecruit=answer)
        if answer == question.correctAnswer:
            count += 1
    return count


@transaction.atomic
def set_test_result(recruit, post_dict):
    """Отмечает в бд, что рекрут прошёл тест, записывает результаты тестов
    рекрута в бд и подсчитывает количество правильных ответов
    """
    recruit.isTested = True
    recruit.save()

    return calculate_test_results(recruit, post_dict)


def get_answers_and_count(recruits):
    """Получение правильных ответов рекрутов
    :param recruits: Recruit Queryset
    :return: Словарь содержащий в качестве ключа id рекрута, в качестве значения
    массив id правильно отвеченных вопросов
    """
    tests = Test.objects.all().order_by('id').values_list(
        'id', 'correctAnswer')
    answers = {}
    # Получение ответов рекрутов и подсчет правильных ответов
    for recr in recruits:
        results = Result.objects.filter(recruit=recr).values_list(
            'question_id', 'answerOfRecruit')
        results_dict = dict(results)
        # id правильных ответов
        correct_questions = [
            question_id for question_id, correct_answer in tests
            if results_dict.get(question_id) == correct_answer]
        answers[recr.id] = correct_questions
    return answers


def get_recruit(recruit_id, is_return_response=False):
    """Возвращает Recruit по id
    :param recruit_id: id рекрута
    :param is_return_response: В случае неудачи возвращать также HttpResponse,
    если True, иначе None
    :return:
    """
    try:
        recruit = Recruit.objects.get(id=recruit_id)
    except Recruit.DoesNotExist:
        if is_return_response:
            return False, None, HttpResponse(simple_html_text.format(
                f"Рекрут с id={recruit_id} не найден!"))
        else:
            return False, None, None
    else:
        return True, recruit, None


def get_object(id, model, is_return_response=False, verbose='Объект'):
    """Возвращает Recruit по id
    :param recruit_id: id рекрута
    :param is_return_response: В случае неудачи возвращать также HttpResponse,
    если True, иначе None
    :return:
    """
    try:
        obj = model.objects.get(id=id)
    except model.DoesNotExist:
        if is_return_response:
            return False, None, HttpResponse(simple_html_text.format(
                f"{verbose} с id={id} не найден!"))
        else:
            return False, None, None
    else:
        return True, obj, None
