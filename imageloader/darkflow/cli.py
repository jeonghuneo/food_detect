from .defaults import argHandler #Import the default arguments
import os
from .net.build import TFNet
import json
import pandas as pd
import csv
from selenium import webdriver
from pytrends.request import TrendReq
import datetime


def cliHandler(image_name):
    FLAGS = argHandler()
    FLAGS.setDefaults()
    #FLAGS.parseArgs(args)

    FLAGS.model = "./cfg/my-tiny-yolo.cfg" # tensorflow model
    # FLAGS.load = "darkflow/bin/tiny-yolo.weights" # tensorflow weights
    
    FLAGS.pbLoad = "./bin/my-tiny-yolo.pb" # tensorflow model
    FLAGS.metaLoad = "./bin/my-tiny-yolo.meta" # tensorflow weights

    # make sure all necessary dirs exist
    def _get_dir(dirs):
        for d in dirs:
            this = os.path.abspath(os.path.join(os.path.curdir, d))
            if not os.path.exists(this): os.makedirs(this)
    
    requiredDirectories = [FLAGS.imgdir, FLAGS.binary, FLAGS.backup, os.path.join(FLAGS.imgdir,'out')]
    if FLAGS.summary:
        requiredDirectories.append(FLAGS.summary)

    _get_dir(requiredDirectories)

    # fix FLAGS.load to appropriate type
    try: FLAGS.load = int(FLAGS.load)
    except: pass

    tfnet = TFNet(FLAGS)
    
    if FLAGS.demo:
        tfnet.camera()
        exit('Demo stopped, exit.')

    if FLAGS.train:
        print('Enter training ...'); tfnet.train()
        if not FLAGS.savepb: 
            exit('Training finished, exit.')

    if FLAGS.savepb:
        print('Rebuild a constant version ...')
        tfnet.savepb(); exit('Done')

#    tfnet.predict() #// 원본
    import cv2
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np


    im = 'C:/img/'+str(image_name) #이미지가 저장된 폴더 위치 + POST형식으로 받은 이미지 이름

    img = cv2.imread(im, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # results =  tfnet.return_predict(img)
    colors = [tuple(255*np.random.rand(3)) for _ in range(10)]

    # for color_img in zip(colors, results):
    #     if result_img['confidence'] > 0.6:
    #         t1 = (result_img['topleft']['x'], result_img['topleft']['y'])
    #         br = (result_img['bottomright']['x'], result_img['bottomright']['y'])
    #         label = result_img['label']

    #         img = cv2.rectangle(img, t1, br, color_img, 7)
    #         img = cv2.putText(img, label, t1, cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,0),2)
    # cv2.imwrite("./polls/static/after.jpg", img)

    result = {}
    result_1 = []
    for color_img, i in zip(colors, range(len(tfnet.return_predict(cv2.imread(im))))):        
        person_exist=False
        if tfnet.return_predict(cv2.imread(im))[i]['confidence'] >0.001: #신뢰도가 50%이상이면 결과로 반환해 준다
            result_1.append(tfnet.return_predict(cv2.imread(im))[i]['label'])
            result.update({i:{'label':tfnet.return_predict(cv2.imread(im))[i]['label'],'confidence':str(tfnet.return_predict(cv2.imread(im))[i]['confidence'])}})
            # if person_exist == True: #사람이 있으면 알고리즘을 끝낸다
            #     break;
            t1 = (tfnet.return_predict(cv2.imread(im))[i]['topleft']['x'], tfnet.return_predict(cv2.imread(im))[i]['topleft']['y'])
            br = (tfnet.return_predict(cv2.imread(im))[i]['bottomright']['x'], tfnet.return_predict(cv2.imread(im))[i]['bottomright']['y'])
            label = tfnet.return_predict(cv2.imread(im))[i]['label']

            img = cv2.rectangle(img, t1, br, color_img, 7)
            img = cv2.putText(img, label, t1, cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,0),2)
    cv2.imwrite("./polls/static/after.jpg", img)


    print(result_1, type(result_1))
    f = open('./ingre.txt','w')
    f.write(str(result_1))
    f.close()
    result = json.dumps(result) #json형태로 반환
    result = json.loads(result)
    result = pd.DataFrame.from_dict(result, orient='index')
    print(result)
    print(type(result))
    #모든 데이터를 넘기는게 아니라 그냥 person유무만 넘겨줘도 될 거 같습니다
    return result

# def cliHandler(args):
#     FLAGS = argHandler()
#     FLAGS.setDefaults()
#     FLAGS.parseArgs(args)

#     # make sure all necessary dirs exist
#     def _get_dir(dirs):
#         for d in dirs:
#             this = os.path.abspath(os.path.join(os.path.curdir, d))
#             if not os.path.exists(this): os.makedirs(this)
    
#     requiredDirectories = [FLAGS.imgdir, FLAGS.binary, FLAGS.backup, os.path.join(FLAGS.imgdir,'out')]
#     if FLAGS.summary:
#         requiredDirectories.append(FLAGS.summary)

#     _get_dir(requiredDirectories)

#     # fix FLAGS.load to appropriate type
#     try: FLAGS.load = int(FLAGS.load)
#     except: pass

#     tfnet = TFNet(FLAGS)
    
#     if FLAGS.demo:
#         tfnet.camera()
#         exit('Demo stopped, exit.')

#     if FLAGS.train:
#         print('Enter training ...'); tfnet.train()
#         if not FLAGS.savepb: 
#             exit('Training finished, exit.')

#     if FLAGS.savepb:
#         print('Rebuild a constant version ...')
#         tfnet.savepb(); exit('Done')

# #    tfnet.predict() #// 원본
# #    return print(내용) print를 return 하는게 의미가 있을까? (어차피 print만 해도 결과값이 보이는데 굳이 return??)
# # 파일경로를 쉽게 만들자(defaults의 경로를 가져오고 싶다)
# # 신뢰도 얼마 이상인 것들만 뽑아내게 하자
# # return 값들 중 하나라도 person이 있으면 True
# # 여러 이미지 파일에 대해서는 어떻게 처리할건지 생각해보자
#     import cv2
#     im = '/home/qwerty1434/python_file/django/imageloader/polls/darkflow_master/sample_img/sample_computer.jpg'
#     person_exist=False
#     for i in range(len(tfnet.return_predict(cv2.imread(im)))):        
#         if tfnet.return_predict(cv2.imread(im))[i]['confidence'] >0.5:
#             if tfnet.return_predict(cv2.imread(im))[i]['label'] == "person":
#                 person_exist = True
#             print(tfnet.return_predict(cv2.imread(im))[i]['label'],tfnet.return_predict(cv2.imread(im))[i]['confidence'],person_exist)
            


def food_recommend(ingre):
    pd.set_option('max_colwidth', 800)
    recipe_df = pd.read_excel('./주재료+부재료+레시피_최종.xlsx')
    # im = './polls/static/before.jpg'
    # data, ingre = cliHandler(im)

    user_ingredients = ingre
    
    # user_ingredients = ['button_mushroom', 'potato']

    # 레시피와 유저의 재료명 교집합 리스트(주재료, 부재료)
    main_ingredients = []
    sub_ingredients = []

    # 레시피와 유저의 겹치는 재료수(주재료, 부재료)
    main_ingredients_cnt = []
    sub_ingredients_cnt = []

    for i in range(0, len(recipe_df)):
        ju = recipe_df['ingredient_ju'][i]
        bu = recipe_df['ingredient_bu'][i]
        # 주재료가 1개 이상일 경우
        if len(set(user_ingredients) & set(ju.split()))>=1:
            main_ingredients.append(list(set(user_ingredients) & set(ju.split())))
            if len(set(user_ingredients) & set(bu.split()))>=1:
                sub_ingredients.append(list(set(user_ingredients) & set(bu.split())))
            else:
                sub_ingredients.append([])
        # 주재료가 없는 경우        
        else:
            main_ingredients.append([])
            sub_ingredients.append([])

        if not main_ingredients[i]:
            main_ingredients_cnt.append(0)
        else:
            main_ingredients_cnt.append(len(main_ingredients[i]))

        if not sub_ingredients[i]:
            sub_ingredients_cnt.append(0)
        else:
            sub_ingredients_cnt.append(len(sub_ingredients[i]))


    recipe_df['user주재료개수'] = main_ingredients_cnt
    recipe_df['user부재료개수'] = sub_ingredients_cnt    

    recommend_recipe = recipe_df.loc[recipe_df['user주재료개수']>=1,:]

    recommend_recipe = recommend_recipe.drop(['Unnamed: 0', '유형분류', '음식분류', '난이도'], axis=1)
    recommend_recipe = recommend_recipe.reset_index()
    del recommend_recipe['index']

    tmp = []
    for i in range(len(recommend_recipe)):
        user_cnt = len(user_ingredients)
        ju_cnt = len(recommend_recipe['ingredient_ju'][i])
        bu_cnt = len(recommend_recipe['ingredient_bu'][i])
        grade = (user_cnt / (ju_cnt + bu_cnt))*1000
#         print(grade)
        tmp.append(grade)

    recommend_recipe['recipe_grade'] = tmp


    # 구글 트렌드 시간대
    a=datetime.datetime.strptime(str('05:00:00'),'%H:%M:%S')
    b=datetime.datetime.strptime(str('09:00:00'),'%H:%M:%S')
    c=datetime.datetime.strptime(str('10:00:00'),'%H:%M:%S')
    d=datetime.datetime.strptime(str('14:00:00'),'%H:%M:%S')
    e=datetime.datetime.strptime(str('15:00:00'),'%H:%M:%S')
    f=datetime.datetime.strptime(str('20:00:00'),'%H:%M:%S')
    g=datetime.datetime.strptime(str('21:00:00'),'%H:%M:%S')


    h=datetime.datetime.strptime(str('04:00:00'),'%H:%M:%S')

    ### 구글 트렌드 데이터 가져오기
    pytrend = TrendReq(hl = 'ko', tz = 540)

    search_list = recommend_recipe.search_name.unique().tolist() # recommend_recipe 검색어 변수 수정

    k = 0

    for i in search_list :
        keyword = [i]  
        pytrend.build_payload(kw_list = keyword, timeframe = 'now 7-d')  # 검색하는동안 시간이 변할 수 있음. 만에하나...

        if k == 0 :
            trend_table = pytrend.interest_over_time().drop('isPartial', axis=1)
        else :
            trend_table = pd.merge(trend_table, pytrend.interest_over_time().drop('isPartial', axis=1), left_index = True, right_index = True, how = 'left')
        k += 1  

    ### 필요한 TIME 파트 추출
    trend_table = trend_table.reset_index()
    trend_table['date'] = [datetime.datetime.strptime(str(i).split(' ')[1], '%H:%M:%S') for i in trend_table.date]

    now = datetime.datetime.now()
    nowtime = now.strftime('%H')

    if 5<=int(nowtime)<=9:
        time ='A'
        start=a
        finish=b
    elif 10<=int(nowtime)<=14:
        time = 'B'
        start=c
        finish=d
    elif 15<=int(nowtime)<=20:
        time = 'C'
        start=e
        finish=f
    else:
        time = 'D'
        start=g
        finish=h

    for i in range(len(trend_table)):
        if time in ['A','B','C'] : 
            if start<trend_table.date[i]<finish:
                True
            else :
                trend_table.drop(i, axis=0, inplace=True)
        else : 
            if finish<trend_table.date[i]<start:
                trend_table.drop(i, axis=0, inplace=True)
            else :
                True

    trend_table = trend_table.reset_index(drop=True)

    ### 구글트렌드 값 평균내서 recommend_recipe 테이블에 병합

    trend_average = trend_table.mean(axis=0).to_frame('average')
    recommend_recipe['average']=[0.0]*len(recommend_recipe)

    for i in range(len(recommend_recipe)) : 
        for j in range(len(trend_average)) : 
            if recommend_recipe.search_name[i] == trend_average.index[j] : 
                recommend_recipe.average[i] = round(trend_average.average[j], 2)
                break
    recommend_trend = recommend_recipe.sort_values(['average', 'recipe_grade'], ascending=False)
    recommend_trend = recommend_trend.reset_index()
    del recommend_trend['index']
    
    recommend_grade = recommend_recipe.sort_values(['recipe_grade', 'average'], ascending=False)
    recommend_grade = recommend_grade.reset_index()
    del recommend_grade['index']
    
    return recommend_trend, recommend_grade


