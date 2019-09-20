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
    im = 'C:/project/imageloader/sample_img/'+str(image_name) #이미지가 저장된 폴더 위치 + POST형식으로 받은 이미지 이름
    result = {}
    for i in range(len(tfnet.return_predict(cv2.imread(im)))):        
        person_exist=False
        if tfnet.return_predict(cv2.imread(im))[i]['confidence'] >0.5: #신뢰도가 50%이상이면 결과로 반환해 준다
            if tfnet.return_predict(cv2.imread(im))[i]['label'] == "person": #사람인지 판단한다
                person_exist = True
            # result.append(tfnet.return_predict(cv2.imread(im))[i]['label'])
            result.update({i:{'label':tfnet.return_predict(cv2.imread(im))[i]['label'],'confidence':str(tfnet.return_predict(cv2.imread(im))[i]['confidence'])}})
            # if person_exist == True: #사람이 있으면 알고리즘을 끝낸다
            #     break;
    result = json.dumps(result) #json형태로 반환
    #모든 데이터를 넘기는게 아니라 그냥 person유무만 넘겨줘도 될 거 같습니다
    return result


def command(ingredients):
    recipe_df = pd.read_excel('./주재료+부재료+레시피_최종.xlsx')

    user_ingredients = cliHandler(image_name)

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
        print(grade)
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
        if start<trend_table.date[i]<finish:
            True
        else :
            trend_table.drop(i, axis=0, inplace=True)

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