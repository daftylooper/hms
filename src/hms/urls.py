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
from utils.views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('task/<uuid:task_id>', TaskView.as_view(), name="Task View"),
    path('hospitals', HospitalList.as_view(), name='Hospital List'),
    path('hospital/<int:pk>', HospitalView.as_view(), name='Hospital View'),
    path('departments', DepartmentList.as_view(), name='Department List'),
    path('department/<int:pk>', DepartmentView.as_view(), name='Department View'),
    path('doctors', DoctorList.as_view(), name='Doctor List'),
    path('doctor/<int:pk>', DoctorView.as_view(), name='Doctor View'),
    path('patients', PatientList.as_view(), name='Patient List'),
    path('patient/<int:pk>', PatientView.as_view(), name='Patient View'),
    path('patient/status/<int:pk>', StatusView.as_view(), name="Status View"),
    path('visits', VisitList.as_view(), name='Visit List'),
    path('visit/<int:pk>', VisitView.as_view(), name='Visit View')
]
