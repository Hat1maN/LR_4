from django.urls import path
from . import views

urlpatterns = [
    path('', views.add_brand, name='add_brand'),         # форма добавления
    path('upload/', views.upload_file, name='upload'),  # загрузка XML
    path('list/', views.list_files, name='list'),       # просмотр всех файлов
    path('ajax/search/', views.ajax_search, name='ajax_search'),
    path('edit/<int:pk>/', views.edit_brand, name='edit_brand'),
    path('delete/<int:pk>/', views.delete_brand, name='delete_brand'),
]


