from django.shortcuts import render
from django.views.generic import TemplateView ,DetailView
import requests, re, pickle, nltk
from django.http import HttpResponseRedirect, HttpResponse
import pandas as pd
from nltk.corpus import stopwords
from django.http import HttpResponse
from django.template import loader
from pprint import  pprint


class homeview(TemplateView):
    template_name = "index.html"


def clean_document(document):
    document = re.sub(r'[\w\.-]+@[\w\.-]+', ' ', document)
    document = re.sub(r'(?:https?:\/\/)?(?:www\.)?[a-z0-9-]+\.(?:com|org)(?:\.[a-z]{2,3})?', ' ', document)
    document = re.sub(r'[a-z0-9-]+\.(?:com|org|io)(?:\.[a-z]{2,3})?/[^\s]+', ' ', document)
    document = re.sub(r'^https?:\/\/.*[\r\n]*', ' ', document)
    document = re.sub('[^A-Za-z .-]+', ' ', document)
    document = ' '.join(document.split())
    return document

def word_freq_dist(document):
    stop = stopwords.words('english') + ['.', '-']
    document = clean_document(document)
    words = nltk.tokenize.word_tokenize(document)
    words = [word.lower() for word in words if word not in stop]
    fdist = nltk.FreqDist(words)
    Freq_Table = pd.DataFrame.from_dict(fdist, orient='index').reset_index().rename(
        columns={'index': 'Keywords', 0: 'Frequency'})
    return Freq_Table

def Score(Freq_Table):
    Unwant_Keyword_list = []
    Freq_Table = Freq_Table.loc[~Freq_Table['Keywords'].isin(Unwant_Keyword_list)]
    Score = Freq_Table['Frequency'].sum()
    return Score


def page_two(request):

    try:
        whole_data = request.session['df']
        print "EDIT DONE"
    except:
        print "NOT EDITED"
        cleaned_text = clean_document(request.POST['big_text'])
        whole_data = word_freq_dist(cleaned_text)
        try:
            request.session['df'] = whole_data
        except:
            pass
    Score_val = Score(whole_data)
    template = loader.get_template('two.html')

    data_dict = whole_data.to_dict()
    keywords =  data_dict['Keywords']
    Frequency =  data_dict['Frequency']
    keywords_to_dict = []
    for i in keywords:
        data_to_send = {
            "key":keywords[i],
            "fre":Frequency[i],
            'index':i
        }
        keywords_to_dict.append(data_to_send)
    context = {
        'whole_data':keywords_to_dict,
        'Score_val':Score_val
    }
    return HttpResponse(template.render(context, request))


def drop_val(request, index):
    dataframe = request.session['df']
    dataframe.drop(dataframe.index(index))
    request.session['df'] = dataframe
    request.session['edit'] = True
    return HttpResponseRedirect('/page_2/')





home = homeview.as_view()
