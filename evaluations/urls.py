from django.urls import path
from . import views

app_name = 'evaluations'

urlpatterns = [
    # Campaigns
    path('campaigns/', views.campaign_list, name='campaign_list'),
    path('campaigns/create/', views.campaign_create, name='campaign_create'),
    
    # Evaluations
    path('my-evaluations/', views.my_evaluations, name='my_evaluations'),
    path('evaluate/<int:employee_id>/', views.evaluate_employee, name='evaluate_employee'),
    path('evaluation/<int:pk>/', views.evaluation_detail, name='evaluation_detail'),
    
    # Goals
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/create/<int:employee_id>/', views.goal_create, name='goal_create'),

    path('self-evaluate/', views.self_evaluate, name='self_evaluate'),          
    path('all/', views.all_evaluations, name='all_evaluations'), 

    path('campaigns/<int:pk>/', views.campaign_detail, name='campaign_detail'),
]