import pandas as pd
import stanza
import numpy as np
from tqdm import tqdm
tqdm.pandas()
data=pd.read_csv('test.csv')
nlp = stanza.Pipeline(lang='en', processors='tokenize,ner')
def non_phrase(text):
    try:
        doc=nlp(text)
        phrases=list(set(i.text for i in doc.ents))
        return phrases
    except:
        return np.nan


data['Description']=data['overviews'].progress_apply(non_phrase)
# data.to_csv('../../Data/final.csv')





















