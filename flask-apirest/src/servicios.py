import os

from flask_restful import Resource, abort, request
import requests
import json
import urllib
import nltk
nltk.download('stopwords') 
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import numpy as np
import transformers 
import time
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from transformers import pipeline

#########################################FUNCIONES############################################

##Normalizacion
def normalizacion(doc):
    doc = re.sub('[^A-Za-z0-9]+', ' ', doc)
    doc = doc.lower()
    doc_tokens = doc.split()  # Tokenización
    list_stopwords = stopwords.words('english') #Eliminacion de stopwords
    for word in doc_tokens:
        if word in list_stopwords:
            doc_tokens.remove(word)
    stemmer = PorterStemmer()  #Proceso de Stemming
    doc_tokens1 = [stemmer.stem(word) for word in doc_tokens]
    doc = doc_tokens1
    return doc

def similitudJaccard(d1,d2):
    simi_jaccard=(len(d1.intersection(d2))) / len(d1.union(d2))
    return simi_jaccard
####################################################################################
class IndexDocs(Resource):
    def get(self, getquery):
        query=[getquery]
        URL = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query='+getquery+'&resultType=core&cursorMark=*&pageSize=100&format=json' #configuramos la url
        data = requests.get(URL)
        json_post = data.json()
        title=[feature["title"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
        keyword=[" ".join(feature["keywordList"]["keyword"]) for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
        authors=[feature["authorString"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
        abstract=[feature["abstractText"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
        id_pub=[feature["id"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
        pubyear=[feature["pubYear"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
        doi=[feature["doi"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
        url=[feature["fullTextUrlList"]["fullTextUrl"][0]["url"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
        ##Inicializacion data
        data_abstract=[]
        data_title=[]
        data_keyword=[]
        data_abstract=data_abstract+query+abstract
        data_title=data_title+query+title
        data_keyword=data_keyword+query+keyword

        ##########################################NORMALIZACION##############################################
        data_normalizados_abstract=[" ".join(normalizacion(data_abstract[i])) for i in range(len(data_abstract))]
        data_normalizados_title = [normalizacion(data_title[i]) for i in range(len(data_abstract))]
        data_normalizados_keyword = [normalizacion(data_keyword[i]) for i in range(len(data_abstract))]
        #########################################SIMILITUD COSENO############################################
        tfidf = TfidfVectorizer().fit_transform(data_normalizados_abstract)
        #Similitud coseno
        simi_coseno_abstract=cosine_similarity(tfidf[0:1], tfidf).flatten()
        ########################################SIMILITUD JACCARD############################################
        simi_jaccard_title=[similitudJaccard(set(data_normalizados_title[0]),set(data_normalizados_title[i])) for i in range(len(data_abstract))]
        simi_jaccard_keyword=[similitudJaccard(set(data_normalizados_keyword[0]),set(data_normalizados_keyword[i])) for i in range(len(data_abstract))]

        similitud_final= (np.array(simi_jaccard_title)*0.10)+ (np.array(simi_jaccard_keyword)*0.20)+(np.array(simi_coseno_abstract)*0.70)
        salida_ordena= np.argsort(-1*similitud_final)

        resultados=[{ "id": id_pub[salida_ordena[i]-1],"doi": doi[salida_ordena[i]-1],"title": title[salida_ordena[i]-1], "author":authors[salida_ordena[i]-1],"pubyear": pubyear[salida_ordena[i]-1],"url": url[salida_ordena[i]-1], "keyword":keyword[salida_ordena[i]-1], "abstract":abstract[salida_ordena[i]-1]} for i in range(1,len(salida_ordena))]

        return resultados, 200

####################################################################################
class ResultSimi(Resource):
    def get(self, getquery1):
        query=[getquery1]
        URL = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query='+getquery1+'&resultType=core&cursorMark=*&pageSize=500&format=json' #configuramos la url
        data = requests.get(URL)
        json_post = data.json()
        title=[feature["title"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
        keyword=[" ".join(feature["keywordList"]["keyword"]) for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
        authors=[feature["authorString"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
        abstract=[feature["abstractText"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
        id_pub=[feature["id"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
        pubyear=[feature["pubYear"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
        doi=[feature["doi"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
        url=[feature["fullTextUrlList"]["fullTextUrl"][0]["url"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
        ##Inicializacion data
        data_abstract=[]
        data_title=[]
        data_keyword=[]
        data_abstract=data_abstract+query+abstract
        data_title=data_title+query+title
        data_keyword=data_keyword+query+keyword
        ##########################################NORMALIZACION##############################################
        data_normalizados_abstract=[" ".join(normalizacion(data_abstract[i])) for i in range(len(data_abstract))]
        data_normalizados_title = [normalizacion(data_title[i]) for i in range(len(data_abstract))]
        data_normalizados_keyword = [normalizacion(data_keyword[i]) for i in range(len(data_abstract))]
        #########################################SIMILITUD COSENO############################################
        tfidf = TfidfVectorizer().fit_transform(data_normalizados_abstract)
        #Similitud coseno
        simi_coseno_abstract=cosine_similarity(tfidf[0:1], tfidf).flatten()
        ########################################SIMILITUD JACCARD############################################
        simi_jaccard_title=[similitudJaccard(set(data_normalizados_title[0]),set(data_normalizados_title[i])) for i in range(len(data_abstract))]
        simi_jaccard_keyword=[similitudJaccard(set(data_normalizados_keyword[0]),set(data_normalizados_keyword[i])) for i in range(len(data_abstract))]

        similitud_final= (np.array(simi_jaccard_title)*0.10)+ (np.array(simi_jaccard_keyword)*0.20)+(np.array(simi_coseno_abstract)*0.70)
        salida_ordena= np.argsort(-1*similitud_final)

        resultados=[{ "id": id_pub[salida_ordena[i]-1],"doi": doi[salida_ordena[i]-1],"title": title[salida_ordena[i]-1], "author":authors[salida_ordena[i]-1],"pubyear": pubyear[salida_ordena[i]-1],"url": url[salida_ordena[i]-1], "keyword":keyword[salida_ordena[i]-1], "abstract":abstract[salida_ordena[i]-1]} for i in range(2,5)]

        return resultados, 200

####################################################################################
class GPT2(Resource):
    
    def get(self, getquery2,abstract1):

        start_time = time.time()
        title=getquery2
        abstract_original=abstract1
        palabras_original=len(abstract_original.split())
        num_palabras=palabras_original

        long_palabras_aumentada = palabras_original + (palabras_original*0.48)
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'gpt2-europe-v3', 'config.json'))
        with open(config_path, "r") as jsonfile:
            data = json.load(jsonfile) # Reading the file
            print("Read successful")
            jsonfile.close()

        data['task_specific_params']['text-generation']['max_length'] = int(long_palabras_aumentada)

        print("Date updated")
        with open(config_path, "w") as jsonfile:
            myJSON = json.dump(data, jsonfile) # Writing to the file
            print("Write successful")
            jsonfile.close()  
        
        #tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        #model = GPT2LMHeadModel.from_pretrained('gpt2')
        #inputs = tokenizer.encode(title, return_tensors='pt')
        #outputs = model.generate(inputs, max_length=200, do_sample=True, temperature = 0.7 , top_k=50)
        #text = tokenizer.decode(outputs[0], skip_special_tokens=True) 

        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'gpt2-europe-v3'))
        resumen = pipeline('text-generation',model=model_path, tokenizer='gpt2')
        ##result = chef('Zuerst Tomaten')[0]['generated_text']
        text=resumen(title)
        print("=== texto gpt2 nuevo modelo ===")
        abstract_gpt2=text[0]['generated_text']
        #print(abstract_gpt2[0]['generated_text'])
        print("without replace")
        print(abstract_gpt2)
        abstract_gpt2 = abstract_gpt2.replace(title+" ", '')
        print("replace")
        print(abstract_gpt2)
        abstract_gpt2 = abstract_gpt2.capitalize()
        print("replace 22")
        print(abstract_gpt2)

        print("**********")
        print("longitud abstract original")
        print(len(abstract_original.split()))
        print(len(abstract_original))
        print("longitud abstract gpt2 nuevo")
        print(len(abstract_gpt2.split()))
        print(len(abstract_gpt2))
        print("**********")

        abstract_final_gpt2 = ''
        abstract_final_gpt2_extra = ''

        i=0
        #pos_busqueda1 = a.rfind("hola")
        pos_final_abstract = abstract_gpt2.rfind(".")
        print(pos_final_abstract)
        print("abstract gpt2", abstract_gpt2)


        for i in range(0,pos_final_abstract+1):
            abstract_final_gpt2 = abstract_final_gpt2 + abstract_gpt2[i]

        data_abstract=[]
        data_abstract.append(abstract_original)
        data_abstract.append(abstract_final_gpt2)
        palabras_gpt2=len(abstract_final_gpt2.split())
        data_normalizados_abstract=[" ".join(normalizacion(data_abstract[i])) for i in range(len(data_abstract))]
        tfidf = TfidfVectorizer().fit_transform(data_normalizados_abstract)
        #Similitud coseno

        simi_coseno_abstract=cosine_similarity(tfidf[0:1], tfidf).flatten()
        #Similitud jaccard
        simi_jaccard_abstract=similitudJaccard(set(data_normalizados_abstract[0]),set(data_normalizados_abstract[1]))
        print(simi_coseno_abstract)
        print("---Tiempo de Procesamiento:  %s seconds ---" % (time.time() - start_time))
        timegpt2=time.time() - start_time
        result={'new_abstract': abstract_final_gpt2,'num_words_original': palabras_original,'num_words_gpt2': palabras_gpt2,'simi_coseno': simi_coseno_abstract[1],'simi_jaccard': simi_jaccard_abstract, 'timeGPT2': timegpt2}
        
        return result,200

