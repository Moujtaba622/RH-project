from django.urls import include
from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentification
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Réinitialisation mot de passe
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             success_url=reverse_lazy('accounts:password_reset_done')
         ),
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url=reverse_lazy('accounts:password_reset_complete')
         ),
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    
    # Assignation de rôle
    path('assign-role/<int:user_id>/', views.assign_role_view, name='assign_role'),
    
    # Gestion des employés
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/deactivate/', views.employee_deactivate, name='employee_deactivate'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('my-team/', views.my_team, name='my_team'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path('employees/<int:employee_id>/contract/create/', views.contract_create, name='contract_create'),
    path('contract/<int:contract_id>/edit/', views.contract_edit, name='contract_edit'),
    path('contract/<int:contract_id>/', views.contract_detail, name='contract_detail'),
    path('payslip/test/<int:employee_id>/', views.generate_payslip_test, name='generate_payslip_test'),
    path('payroll/dashboard/', views.payroll_dashboard, name='payroll_dashboard'),
    path('payslip/<int:payslip_id>/edit/', views.edit_payslip, name='edit_payslip'),
    path('payslip/<int:payslip_id>/pdf/', views.payslip_pdf, name='payslip_pdf'),
    path('my-payslips/', views.my_payslips, name='my_payslips'),
    path('payslip/<int:payslip_id>/', views.payslip_detail, name='payslip_detail'),
    path('reports/', views.reports, name='reports'),
    path('reports/export-excel/', views.export_employees_excel, name='export_employees_excel'),
    
]