from django.db import models


class Planet(models.Model):
    """Модель планет"""
    planetID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, verbose_name='Название планеты')

    @classmethod
    def get_choices(cls):
        """Возвращает id и названия всех планет"""
        return [(planet.planetID, planet.name)
                for planet in cls.objects.all().only('planetID', 'name')]


class Sith(models.Model):
    """Модель ситхов (учителей для рекрутов)"""
    name = models.CharField(max_length=30, verbose_name='Имя')
    planet = models.ForeignKey(Planet, on_delete=models.CASCADE)

    @property
    def hands_of_shadow(self):
        """Руки Тени у ситха"""
        hands_of_shadow = Recruit.objects.filter(
            isHandOfShadow=True, sith_master=self)
        count_hands_of_shadow = hands_of_shadow.count()
        return hands_of_shadow, count_hands_of_shadow


class Recruit(models.Model):
    """Модель рекрутов (учеников)"""
    name = models.CharField(max_length=30, verbose_name='Имя')
    planet = models.ForeignKey(Planet, on_delete=models.CASCADE)
    age = models.PositiveSmallIntegerField(verbose_name='Возраст')
    email = models.EmailField(verbose_name='Электронная почта')
    isTested = models.BooleanField(
        default=False, verbose_name='Пройден ли тест')
    isHandOfShadow = models.BooleanField(
        default=False, verbose_name='Является ли Рукой Тени')
    sith_master = models.ForeignKey(Sith, on_delete=models.CASCADE, null=True)

    @classmethod
    def get_not_tested_recruit_choices(cls):
        """Возвращает id и имя рекрутов, не сдавших тест"""
        return [(recr.id, recr.name)
                for recr in cls.objects.filter(isTested=False)]


class Test(models.Model):
    """Вопросы и ответы теста"""
    question = models.CharField(max_length=100, verbose_name='Вопрос')
    correctAnswer = models.BooleanField(verbose_name='Правильный ответ')


class Result(models.Model):
    """Результаты рекрутов при ответе на тест"""
    answerOfRecruit = models.BooleanField('Ответ')
    recruit = models.ForeignKey(Recruit, on_delete=models.CASCADE)
    question = models.ForeignKey(Test, on_delete=models.CASCADE)
