from django.http import HttpResponseRedirect , HttpResponse
from django.shortcuts import render , redirect
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import PhotoForm
import sys
from darkflow.cli import cliHandler
from darkflow.cli import food_recommend
import numpy as np
import pandas as pd
import cv2
from PIL import Image
import ast


@csrf_exempt
def index(request):
    return render(request,'polls/index.html')


@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            print(form)
            # return render(request, 'polls/index.html', {'form': form})
    else:
        form =PhotoForm()
    image_name = request.FILES['photo']
    fname = 'C:/img/'+str(image_name)
    im = Image.open(fname)
    im.save('./polls/static/before.jpg')
    # im.show()
    data, ingre = cliHandler(image_name)
    # pd.set_option('colheader_justify', 'center')
    # return HttpResponse(cliHandler(image_name))

    return render(request, 'polls/upload_file.html')



@csrf_exempt
def recommend(request):
    # image_name = './polls/static/before.jpg'
    # data, ingre = cliHandler(image_name)
    r = open('./ingre.txt','r')
    ingre_1 = r.readline()
    ingre = ast.literal_eval(ingre_1)
    print(ingre, type(ingre))
    re_trend, re_grade = food_recommend(ingre)
    re_trend = re_trend[{'레시피이름', 'URL'}].head()
    re_grade = re_grade[{'레시피이름', 'URL'}].head()
    re_trend.index = np.arange(1,len(re_trend)+1)
    re_grade.index = np.arange(1,len(re_grade)+1)
    
    # re_trend['URL'] = re_trend['URL'].apply(lambda x: '<a href="{0}">link</a>'.format(x))
    # re_grade['URL'] = re_grade['URL'].apply(lambda x: '<a href="{0}">link</a>'.format(x))
    re_trend = pd.DataFrame(re_trend, columns=['레시피이름','URL'])
    re_grade = pd.DataFrame(re_grade, columns=['레시피이름','URL'])
    pd.set_option('colheader_justify', 'center')
    # print(re_grade.to_html())
    return render(request, 'polls/recommend.html', {'trend':re_trend.to_html(render_links=True, classes='mystyle'), 
        'grade':re_grade.to_html(render_links=True, classes='mystyle')})



