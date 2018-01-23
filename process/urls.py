from django.conf.urls import url
from . import views
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm




urlpatterns = [
	url(r'^$',views.home,name='home'),
    url(r'page_2/', views.page_two, name='page_two'),


]