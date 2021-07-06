from datetime import datetime
from django.db import models

class surveyUser(models.Model):
    ph_no = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100, blank=True)
    visit_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.ph_no

def question_idx_path(instance, filename):
    filename = filename.split('.amr')[0]
    return '{0}_{1}.amr'.format(filename, instance.date)

class surveyQuestion(models.Model):
    question_id = models.AutoField(primary_key=True)
    # user = models.ForeignKey(surveyUser, on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    answer = models.CharField(max_length=200)
    intent = models.CharField(max_length=100, default='')
    entity = models.CharField(max_length=100, default='')
    audio = models.FileField(upload_to=question_idx_path, default="myaudio.mp3", blank=True)
    date = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return self.question
