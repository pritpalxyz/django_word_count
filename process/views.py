from django.shortcuts import render
from django.views.generic import TemplateView ,DetailView
import requests, re, pickle, nltk
from django.http import HttpResponseRedirect, HttpResponse
import pandas as pd
from nltk.corpus import stopwords
from django.http import HttpResponse
from django.template import loader
import uuid, os
from pprint import  pprint


class homeview(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        try:
            file_name = self.request.session['df']
            del self.request.session['df']
            os.remove(file_name)
        except:
            pass
        return context


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
        file_name = request.session['df']
        whole_data = pd.read_pickle(file_name)
        print "EDIT DONE"
    except:
        print "NOT EDITED"
        cleaned_text = clean_document(request.POST['big_text'])
        whole_data = word_freq_dist(cleaned_text)
        file_name = "{0}.pkl".format(str(uuid.uuid4()))
        whole_data.to_pickle(file_name)
        request.session['df'] = file_name
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
    file_name = request.session['df']
    dataframe = pd.read_pickle(file_name)
    # dataframe = pd.DataFrame([dataframe])
    print dataframe
    # dataframe.drop(dataframe.index(index))
    index = int(index)
    dataframe = dataframe.drop(dataframe.index[[index,]])
    dataframe = dataframe.reset_index(drop=True)
    dataframe.to_pickle(file_name)
    request.session['df'] = file_name
    request.session['edit'] = True
    return HttpResponseRedirect('/page_2/')





home = homeview.as_view()
