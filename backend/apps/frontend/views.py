from django.shortcuts import render

def dashboard_view(request):
    return render(request, 'dashboard.html')

def etl_view(request):
    return render(request, 'etl.html')
