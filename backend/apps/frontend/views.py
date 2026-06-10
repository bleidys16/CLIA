from django.shortcuts import render, redirect

def login_view(request):
    return render(request, 'login.html')

def dashboard_view(request):
    return render(request, 'dashboard.html')

def etl_view(request):
    return render(request, 'etl.html')
