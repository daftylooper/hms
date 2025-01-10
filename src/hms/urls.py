"""
URL configuration for hms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from hospital.views import *
from doctor.views import *
from patient.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hospitals', HospitalList.as_view(), name='Hospital List'),
    path('hospital/<int:pk>', HospitalView.as_view(), name='Hospital View'),
    path('departments', DepartmentList.as_view(), name='Department List'),
    path('department/<int:pk>', DepartmentView.as_view(), name='Department View'),
    path('doctors', DoctorList.as_view(), name='Doctor List'),
    path('doctor/<int:pk>', DoctorView.as_view(), name='Doctor View'),
    path('patients', PatientList.as_view(), name='Patient List'),
    path('patient/<int:pk>', PatientView.as_view(), name='Patient View'),
    path('visits', VisitList.as_view(), name='Visit List'),
    path('visit/<int:pk>', VisitView.as_view(), name='Visit View'),
]
