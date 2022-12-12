import pandas as pd
import re
import collections
from tmdbv3api import TMDb
from tmdbv3api import Movie
import numpy as np
import time
data=pd.read_csv('../../Data/IMDb_All_Genres_etf_clean1.csv')
data=data[['Movie_Title','Year','Director','Actors','main_genre','side_genre']]
data=data.drop_duplicates(subset=['Movie_Title'])

cand=set()
for _,row in data.iterrows():
    g=row['side_genre'].split(',')
    g.append(row['main_genre'])
    for c in g:
        if c.strip() not in cand:
            cand.add(c.strip())
m=collections.defaultdict(dict)
for _,row in data.iterrows():
    g=row['side_genre'].split(',')
    g.append(row['main_genre'])
    g=[i.strip() for i in g]
    for c in cand:
        if c in g:
            m[row['Movie_Title']][c]=1
        else:
            m[row['Movie_Title']][c] = 0
data=data.reset_index()[['Movie_Title','Year','Director','Actors']]
dd=pd.DataFrame(m)
dd=dd.transpose()
dd=dd.reset_index()
data=pd.merge(left=data,right=dd,left_on='Movie_Title',right_on='index')
data=data.drop(columns=['index'])
print(data.head())

start=time.time()
tmdb = TMDb()
tmdb.api_key = '117ef5dfd35b363340e9a7bd23dc8ce5'
tmdb.language = 'en'
tmdb.debug = True
# print(data.columns)
overviews=[]
movie = Movie()

c=0
for _,row in data.iterrows():
    c+=1
    r=False
    # print(row['Movie_Title'])
    try:
        results=movie.search(row['Movie_Title'])
        for res in results:
            if res.release_date.split('-')[0]==str(row['Year']):
                r=True
                overviews.append(res.overview)
                break
        if not r:
            overviews.append(np.nan)
    except:
        overviews.append(np.nan)
    if c%500==0:
        print(time.time()-start)
# print(len(overviews))

o=pd.DataFrame(overviews,columns=['overviews'])
data=pd.concat([data,o],axis=1)
# print(data.columns)
# print(data.shape)
# data.to_csv('test.csv')

