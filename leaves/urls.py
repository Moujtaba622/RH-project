from django.urls import path
from . import views

urlpatterns = [
    path('request/', views.request_leave, name='request_leave'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('balance/', views.leave_balance, name='leave_balance'),
    path('pending/', views.pending_requests, name='pending_requests'),
    path('approve/<int:pk>/', views.approve_leave, name='approve_leave'),
    path('reject/<int:pk>/', views.reject_leave, name='reject_leave'),
    path('payslip/test/<int:employee_id>/', views.generate_payslip_test, name='generate_payslip_test'),
]