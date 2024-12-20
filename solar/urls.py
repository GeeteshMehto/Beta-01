"""ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('solarbill/', views.solarbill, name='solarbill'),
    path('calculate-solar', views.calculate_solar, name='calculate_solar'),
    path('predict_view/', views.predict_view, name='predict_view'),
    path('gen/', views.gen, name='gen'),
    # path('dashboard/', views.dashboard, name='dashboard'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
