from django.shortcuts import render
from django.http import HttpResponse, HttpResponsePermanentRedirect
from recruiting_app.helpers import (
    send_email_to_recruit, get_answers_and_count, simple_html_text,
    get_object, set_test_result)
from .forms import RecruitForm, RecruitChoiceForm
from .models import Sith, Recruit, Result, Planet, Test


def index(request):
    return render(request, "index.html")


def recruit(request):
    if request.method == "GET":
        context_data = dict(
            userform=RecruitForm(),
            choiceform=RecruitChoiceForm(),
            count_without_test=Recruit.objects.filter(isTested=False).count()
        )
        return render(request, "recruit.html", context=context_data)
    else:
        userform = RecruitForm(request.POST)
        if userform.is_valid():
            new_recruit = Recruit.objects.create(
                name=userform.cleaned_data["name"],
                planet=Planet.objects.get(
                    planetID=int(userform.cleaned_data["planet"])),
                age=int(userform.cleaned_data["age"]),
                email=userform.cleaned_data["email"]
            )
            return HttpResponsePermanentRedirect(
                "/testpage/{0}".format(new_recruit.id))
        else:
            return HttpResponse('Данные были введены неправильно! '
                                'Вернитесь и повторите ввод данных.')


def index(request):
    return render(request, "index.html")


def choice(request):
    if request.method == "POST":
        id = int(request.POST.get("recruit"))
        return HttpResponsePermanentRedirect("/testpage/{0}".format(id))
    else:
        return HttpResponse(simple_html_text.format("Произошла ошибка."))


def testpage(request, recruit_id):
    success, recruit, err = get_object(recruit_id, Recruit, True, 'Рекрут')
    if not success:
        return err

    if recruit.isTested or Result.objects.filter(recruit=recruit).exists():
        return HttpResponse(simple_html_text.format(
            f"{recruit.name}! Вы уже проходили этот тест!"))

    if request.method == "GET":
        context_data = dict(
            name=recruit.name,
            questions=Test.objects.all().values()
        )
        return render(request, "testpage.html", context=context_data)
    else:
        correct_count = set_test_result(recruit, request.POST)
        message = "Уважаемый, {0}! Вы набрали {1} баллов за тест".format(
            recruit.name, correct_count)
        return HttpResponse(simple_html_text.format(message))


def sith(request):
    sith_all = Sith.objects.all().select_related('planet')
    return render(request, "sith.html", context={"siths": sith_all})


def sith_office(request, sith_id):
    success, sith, err = get_object(sith_id, Sith, True, 'Ситх')
    if not success:
        return err

    if request.method == "GET":
        hands_of_shadow, count_hands_of_shadow = sith.hands_of_shadow

        # Протестированные рекруты с той же планеты
        recruits_with_test = Recruit.objects.filter(
            planet=sith.planet, isTested=True, isHandOfShadow=False)

        questions = Test.objects.all().order_by('id').values_list('id',
                                                                  'question')
        questions_count = questions.count()
        # Получение правильных ответов рекрутов
        answers = get_answers_and_count(recruits_with_test)

        # Передача параметров
        data = {
            "sith": sith,
            "recruits": recruits_with_test,
            "num": range(questions.count()),
            "questions": questions,
            "questions_count": questions_count,
            "answers": answers,
            "hands_of_shadow": hands_of_shadow,
            "count_hands_of_shadow": count_hands_of_shadow
        }
        return render(request, "sith_office.html", context=data)
    else:
        recr_id = request.POST.get("id")
        success, recr, err = get_object(recr_id, Recruit, True, 'Рекрут')
        if not success:
            return err

        Recruit.objects.filter(id=recr_id).update(
            isHandOfShadow=True, sith_master=sith)
        is_sended = send_email_to_recruit(sith, recr)
        if is_sended:
            message = "На его почту отправлено почтовое сообщение."
        else:
            message = "Однако возникли проблемы с отправкой почтового сообщения."
        return HttpResponse(simple_html_text.format(
            'Теперь данный рекрут входит в Орден Ситхов. ' + message))


def sith_info(request):
    siths = Sith.objects.all().order_by("id")
    # Количество рук Тени у ситха
    count = {}
    for sith in siths:
        count[sith.id] = Recruit.objects.filter(
            isHandOfShadow=True, sith_master=sith).count()
    data = {"siths": siths, "count": count}
    return render(request, "sith_info.html", context=data)
