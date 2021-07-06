import os
import sys

import pandas as pd

from ast import literal_eval
from django.shortcuts import render

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
 
from vsurvey.models import surveyQuestion, surveyUser
from vsurvey.serializers import questionSerializer, userSerializer
from rest_framework.decorators import api_view
from vsurvey.utils_polyglot import get_loc_final, get_name_final
from vsurvey.utils import get_month, findYesNo, findDate, get_age

@api_view(['POST'])
def establish_connection(request):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    questions_df = pd.read_excel(os.path.join(base_dir, 'vsurvey_questions.xlsx')).fillna('') # TODO : Change this hard-coded name
    questions = questions_df['Question Name'].str.strip().tolist()
    intents = questions_df['Intent'].str.strip().tolist()
    question_idx = 1
    return JsonResponse({'संदेश': questions[0]+questions[question_idx], 'question_idx':question_idx}, status=200)

@api_view(['POST'])
def get_entity(request):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    questions_df = pd.read_excel(os.path.join(base_dir, 'vsurvey_questions.xlsx')).fillna('') # TODO : Change this hard-coded name
    questions = questions_df['Question Name'].str.strip().tolist()
    intents = questions_df['Intent'].str.strip().tolist()
    question_idx = int(request.POST['question_idx'].strip())

    intent = intents[question_idx]
    answer = request.POST['answer'].strip()
    audio = request.FILES['file1']
    entity = ''
    
    if intent == 'get_name':
        entity = get_name_final(answer)
    elif intent == 'get_loc':
        entity = get_loc_final(answer)
    elif intent == 'get_number':
        entity = get_month(answer)
    elif intent == 'get_yes_no':
        entity = findYesNo(answer)
    elif intent == 'get_date':
        entity = findDate(answer)
    elif intent == 'get_age':
        entity = get_age(answer)

    question_in_db = surveyQuestion(question=questions[question_idx], answer=answer, intent=intent, entity=entity, audio=audio)
    question_in_db.save()
    question_idx += 1
    try:
        return JsonResponse({'संदेश':(entity), 'अगला प्रश्न': questions[question_idx], 'question_idx':question_idx}, status=200)
    except:
        return JsonResponse({'संदेश': "end of survey"}, status=300)

@api_view(['POST'])
def test_api(request):
    print("Got the test case!")
    return JsonResponse({'message': "end of survey"}, status=300)
