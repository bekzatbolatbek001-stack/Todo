from django.contrib import admin # Проверь этот импорт
from django.urls import path
from tasks.views import users_page

urlpatterns = [
    path('admin/', admin.site.urls),          # <--- ЭТОЙ СТРОКИ У ТЕБЯ НЕТ
    path('users/', users_page, name='users_list'),
]
