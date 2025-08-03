"""
URL configuration for interview_bot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from bot.views import (
    homepage, login_view, signup_view, logout_view, 
    admin_dashboard, candidate_dashboard,
    job_description_create, job_description_edit, job_description_delete,
    assign_interview, start_interview, submit_response, interview_results
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    
    # Dashboard URLs
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('candidate-dashboard/', candidate_dashboard, name='candidate_dashboard'),
    
    # Job Description Management URLs
    path('job-description/create/', job_description_create, name='job_description_create'),
    path('job-description/edit/<int:jd_id>/', job_description_edit, name='job_description_edit'),
    path('job-description/delete/<int:jd_id>/', job_description_delete, name='job_description_delete'),
    
    # Interview Assignment URLs
    path('assign-interview/', assign_interview, name='assign_interview'),
    
    # Interview Session URLs
    path('interview/start/<int:assignment_id>/', start_interview, name='start_interview'),
    path('interview/submit/<str:session_id>/', submit_response, name='submit_response'),
    path('interview-results/<int:assignment_id>/', interview_results, name='interview_results'),
    
    # Root URL - homepage
    path('', homepage, name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
