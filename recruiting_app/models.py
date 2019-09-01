from django.db import models


class Planet(models.Model):
    planetID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)


class Sith(models.Model):
    name = models.CharField(max_length=30)
    planet = models.ForeignKey(Planet, on_delete=models.CASCADE)


class Recruit(models.Model):
    name = models.CharField(max_length=30)
    planet = models.ForeignKey(Planet, on_delete=models.CASCADE)
    age = models.PositiveSmallIntegerField()
    email = models.EmailField()
    isTested = models.BooleanField(default=False)
    isHandOfShadow = models.BooleanField(default=False)
    sith_master = models.ForeignKey(Sith, on_delete=models.CASCADE, null=True)


class Test(models.Model):
    question = models.CharField(max_length=100)
    correctAnswer = models.BooleanField()


class Result(models.Model):
    answerOfRecruit = models.BooleanField()
    recruit = models.ForeignKey(Recruit, on_delete=models.CASCADE)
    question = models.ForeignKey(Test, on_delete=models.CASCADE)
