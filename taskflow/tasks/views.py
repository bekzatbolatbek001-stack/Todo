from django.shortcuts import render
from django.contrib.auth.models import User

def users_page(request):
    users = User.objects.all()
    # Убедись, что путь к шаблону правильный.
    # Если файл лежит в templates/tasks/users.html, то пишем так:
    return render(request, 'tasks/users.html', {'users': users})
