from django.core.mail import send_mail
from django.shortcuts import render
from django.http import HttpResponse, HttpResponsePermanentRedirect
from recruiting.settings import EMAIL_HOST_USER
from .forms import RecruitForm, RecruitChoiceForm
from .models import Sith, Recruit, Result, Planet, Test


def index(request):
    return render(request, "index.html")


def recruit(request):
    if request.method == "GET":
        userform = RecruitForm()
        choiceform = RecruitChoiceForm()
        count_without_test = Recruit.objects.filter(isTested=False).count()
        return render(request, "recruit.html",
                      context={"form": userform, "choiceform": choiceform, "count_without_test": count_without_test})
    else:
        userform = RecruitForm(request.POST)
        if userform.is_valid():
            name = userform.cleaned_data["name"]
            planet = Planet.objects.get(planetID=int(userform.cleaned_data["planet"]))
            age = int(userform.cleaned_data["age"])
            email = userform.cleaned_data["email"]
            newrecruit = Recruit(name=name, planet=planet, age=age, email=email)
            newrecruit.save()
            return HttpResponsePermanentRedirect("/testpage/{0}".format(newrecruit.id))
        else:
            return HttpResponse("Данные были введены неправильно! Вернитесь и повторите ввод данных.")


def choice(request):
    if request.method == "POST":
        id = int(request.POST.get("recruit"))
        return HttpResponsePermanentRedirect("/testpage/{0}".format(id))
    else:
        html_page = r"<h2 style='text-align: center;'>{0}<h2><p><a style='display: block;text-align:center;' href='/'>Перейти на главную страницу</a></p>"
        return HttpResponse(html_page.format("Произошла ошибка."))


def testpage(request, recruit_id):
    if request.method == "GET":
        recruit = Recruit.objects.get(id=recruit_id)
        if not recruit.isTested:
            questions = Test.objects.all()
            return render(request, "testpage.html", context={"name": recruit.name, "questions": questions})
        else:
            html_page = r"<h2 style='text-align: center;'>{0}<h2><p><a style='display: block;text-align:center;' href='/'>Перейти на главную страницу</a></p>"
            message = "Уважаемый, {0}! Вы уже проходили этот тест!".format(recruit.name)
            return HttpResponse(html_page.format(message))
    else:
        recruit = Recruit.objects.get(id=recruit_id)
        recruit.isTested = True
        recruit.save()
        count = 0
        for i in Test.objects.all().values("id"):
            answer = request.POST.get("question{0}".format(i["id"]))
            answer = True if answer == "True" else False  # Перевод в bool
            test = Test.objects.get(id=i["id"])
            if Result.objects.filter(recruit=recruit, question=test).count() == 0:
                Result.objects.create(recruit=recruit, question=test, answerOfRecruit=answer)
            if answer == test.correctAnswer:
                count += 1
        html_page = r"<h2 style='text-align: center;'>{0}<h2><p><a style='display: block;text-align:center;' href='/'>Перейти на главную страницу</a></p>"
        message = "Уважаемый, {0}! Вы набрали {1} баллов за тест".format(recruit.name, str(count))
        return HttpResponse(html_page.format(message))


def sith(request):
    sith_all = Sith.objects.all()
    return render(request, "sith.html", context={"siths": sith_all})


# Получение ответов рекрутов и подсчет правильных ответов
def get_answers_and_count(sith_id):
    sith = Sith.objects.get(id=sith_id)
    recruits = Recruit.objects.filter(planet=sith.planet, isTested=True, isHandOfShadow=False)
    test = Test.objects.all().order_by("id")
    # Вопросы и правильные ответы
    qa = []
    for t in test:
        qa.append([t.question, t.correctAnswer])
    # Получение ответов рекрутов и подсчет правильных ответов
    answers = {}
    for rec in recruits:
        res = Result.objects.filter(recruit=rec).order_by("question")
        temp = []
        correct_count = 0
        for i in range(res.count()):
            temp.append(res[i].answerOfRecruit)
            if res[i].answerOfRecruit == qa[i][1]:
                correct_count += 1
        temp.append(correct_count)
        answers[rec.id] = temp
    return qa, answers


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


def sith_office(request, sith_id):
    if request.method == "GET":
        sith = Sith.objects.get(id=sith_id)
        recruits = Recruit.objects.filter(planet=sith.planet, isTested=True, isHandOfShadow=False)
        question_count = Test.objects.all().count()
        count_hands_of_shadow = Recruit.objects.filter(sith_master=sith_id).count()  # Количество рук Тени у ситха
        # Получение ответов рекрутов и подсчет правильных ответов
        qa, answers = get_answers_and_count(sith_id)
        hands_of_shadow = Recruit.objects.filter(isHandOfShadow=True, sith_master=sith)
        # Передача параметров
        data = {"sith": sith, "recruits": recruits, "question_count": question_count, "num": range(question_count),
                "qa": qa, "answers": answers, "count_hands_of_shadow": count_hands_of_shadow,
                "hands_of_shadow": hands_of_shadow}
        return render(request, "sith_office.html", context=data)
    else:
        sith = Sith.objects.get(id=sith_id)
        recr_id = request.POST.get("id")
        recr = Recruit.objects.get(id=recr_id)
        Recruit.objects.filter(id=recr_id).update(isHandOfShadow=True, sith_master=sith)
        issended = send_email_to_recruit(sith, recr)
        html_page = r"<h2 style='text-align: center;'>{0}<h2><p><a style='display: block;text-align:center;' href='/'>Перейти на главную страницу</a></p>"
        if issended:
            message = "Теперь данный рекрут входит в Орден Ситхов. На его почту отправлено почтовое сообщение."
        else:
            message = "Теперь данный рекрут входит в Орден Ситхов. Однако возникли проблемы с отправкой почтового сообщения."
        return HttpResponse(html_page.format(message))


def sith_info(request):
    sith = Sith.objects.all().order_by("id")
    count = {}  # Количество рук Тени у ситха
    for recruit in Recruit.objects.all():
        if recruit.sith_master is not None:
            if recruit.sith_master.id in count.keys():
                count[recruit.sith_master.id] = count[recruit.sith_master.id] + 1
            else:
                count[recruit.sith_master.id] = 1
    moreone = len(count.keys())
    for s in sith:
        if s.id not in count.keys():
            count[s.id] = 0
    # Передача параметров
    data = {"sith": sith, "count": count, "moreone": moreone}
    return render(request, "sith_info.html", context=data)
