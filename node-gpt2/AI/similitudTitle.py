import sys
import requests
import json
import urllib
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
import re
import numpy as np
#start_time = time.time()

query=[sys.argv[1]]
querySearch=sys.argv[1]

URL = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query='+str(querySearch)+'&resultType=core&cursorMark=*&pageSize=15&format=json' #configuramos la url
#solicitamos la información y guardamos la respuesta en data.
data = requests.get(URL)
#Json en String - Primera forma
json_post = data.json()
'''print(json_post)'''

title=[feature["title"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
keyword=[" ".join(feature["keywordList"]["keyword"]) for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
authors=[feature["authorString"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
abstract=[feature["abstractText"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
id_pub=[feature["id"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
pubyear=[feature["pubYear"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
doi=[feature["doi"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]
url=[feature["fullTextUrlList"]["fullTextUrl"][0]["url"] for feature in json_post["resultList"]["result"] if "keywordList" in feature and "abstractText" in feature and "authorString" in feature and "title" in feature and "pubYear" in feature and "doi" in feature and "id" in feature and "fullTextUrlList" in feature]

#####################################################################################################
#########################################FUNCIONES############################################
#####################################################################################################
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

#####################################################################################################
##########################################ANTECEDENTES###############################################
#####################################################################################################

##Inicializacion data
data_abstract=[]
data_title=[]
data_keyword=[]
data_abstract=data_abstract+query+abstract
data_title=data_title+query+title
data_keyword=data_keyword+query+keyword
#print(data_keyword)

#####################################################################################################
##########################################NORMALIZACION##############################################
#####################################################################################################
#Ejecucion de la normalizacion
data_normalizados_abstract=[" ".join(normalizacion(data_abstract[i])) for i in range(len(data_abstract))]
data_normalizados_title = [normalizacion(data_title[i]) for i in range(len(data_abstract))]
data_normalizados_keyword = [normalizacion(data_keyword[i]) for i in range(len(data_abstract))]
#####################################################################################################
#########################################SIMILITUD COSENO############################################
#####################################################################################################
from sklearn.feature_extraction.text import TfidfVectorizer
tfidf = TfidfVectorizer().fit_transform(data_normalizados_abstract)
#Similitud coseno
from sklearn.metrics.pairwise import cosine_similarity
simi_coseno_abstract=cosine_similarity(tfidf[0:1], tfidf).flatten()
#####################################################################################################
########################################SIMILITUD JACCARD############################################
#####################################################################################################
simi_jaccard_title=[similitudJaccard(set(data_normalizados_title[0]),set(data_normalizados_title[i])) for i in range(len(data_abstract))]
simi_jaccard_keyword=[similitudJaccard(set(data_normalizados_keyword[0]),set(data_normalizados_keyword[i])) for i in range(len(data_abstract))]
similitud_final= (np.array(simi_jaccard_title)*0.10)+ (np.array(simi_jaccard_keyword)*0.20)+(np.array(simi_coseno_abstract)*0.70)
salida_ordena= np.argsort(-1*similitud_final)

resultados=[{ "id": id_pub[salida_ordena[i]-1],"doi": doi[salida_ordena[i]-1],"title": title[salida_ordena[i]-1], "author":authors[salida_ordena[i]-1],"pubyear": pubyear[salida_ordena[i]-1],"url": url[salida_ordena[i]-1], "keyword":keyword[salida_ordena[i]-1], "abstract":abstract[salida_ordena[i]-1]} for i in range(2,5)]
sendjson=json.dumps(resultados)
print (sendjson, end="")

#print("---Tiempo de Procesamiento:  %s seconds ---" % (time.time() - start_time))
