from django.urls import path
from . import views

urlpatterns = [
    path('', views.add_brand, name='add_brand'),         # форма добавления
    path('upload/', views.upload_file, name='upload'),  # загрузка XML
    path('list/', views.list_files, name='list'),       # просмотр всех файлов
]
