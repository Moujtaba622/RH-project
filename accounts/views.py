from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from decimal import Decimal
from xhtml2pdf import pisa
from django.core.mail import send_mail
from django.conf import settings

from .models import CustomUser, Contract, Payslip
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, UserRoleForm,
    EmployeeForm, EmployeeStatusForm, ContractForm
)
from leaves.models import LeaveRequest


# ============ PERMISSION HELPERS ============

def is_admin(user):
    return user.role == 'ADMIN'

def is_manager_or_admin(user):
    return user.role in ['ADMIN', 'MANAGER']


# ============ AUTHENTICATION ============

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Compte créé avec succès !')
            return redirect('accounts:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bienvenue {user.get_full_name()} !')
            return redirect('accounts:dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Vous êtes déconnecté.')
    return redirect('accounts:login')


@login_required
def assign_role_view(request, user_id):
    if request.user.role != 'ADMIN':
        messages.error(request, 'Accès non autorisé.')
        return redirect('accounts:dashboard')
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Rôle de {user.get_full_name()} mis à jour.')
            return redirect('/admin/')
    else:
        form = UserRoleForm(instance=user)
    return render(request, 'accounts/assign_role.html', {'form': form, 'target_user': user})


# ============ DASHBOARD ============

@login_required
def dashboard(request):
    context = {
        'user': request.user,
        'role': request.user.role,
    }
    if request.user.role == 'ADMIN':
        context['total_employees'] = CustomUser.objects.filter(role='EMPLOYEE').count()
        context['total_managers'] = CustomUser.objects.filter(role='MANAGER').count()
        context['active_employees'] = CustomUser.objects.filter(status='ACTIVE').count()
    elif request.user.role == 'MANAGER':
        context['team_size'] = CustomUser.objects.filter(manager=request.user).count()
    return render(request, 'accounts/dashboard.html', context)


# ============ EMPLOYEE MANAGEMENT ============

@login_required
@user_passes_test(is_admin)
def employee_list(request):
    employees = CustomUser.objects.all().order_by('first_name', 'last_name')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    department_filter = request.GET.get('department', '')
    search_query = request.GET.get('search', '')
    if role_filter:
        employees = employees.filter(role=role_filter)
    if status_filter:
        employees = employees.filter(status=status_filter)
    if department_filter:
        employees = employees.filter(department__icontains=department_filter)
    if search_query:
        employees = employees.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(employee_id__icontains=search_query)
        )
    paginator = Paginator(employees, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'employees': page_obj,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'department_filter': department_filter,
        'search_query': search_query,
        'total_count': employees.count(),
        'role_choices': CustomUser.ROLE_CHOICES,
        'status_choices': CustomUser.STATUS_CHOICES,
    }
    return render(request, 'accounts/employee_list.html', context)


@login_required
@user_passes_test(is_admin)
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            from django.utils.crypto import get_random_string
            temp_password = get_random_string(length=10)
            user.set_password(temp_password)
            user.save()
            messages.success(request, f'Employé {user.get_full_name()} ajouté. Mot de passe temporaire: {temp_password}')
            return redirect('accounts:employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'accounts/employee_form.html', {'form': form, 'title': 'Ajouter un employé'})


@login_required
@user_passes_test(is_admin)
def employee_edit(request, pk):
    employee = get_object_or_404(CustomUser, id=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'Employé {employee.get_full_name()} modifié avec succès.')
            return redirect('accounts:employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'accounts/employee_form.html', {'form': form, 'title': 'Modifier employé', 'employee': employee})


@login_required
@user_passes_test(is_admin)
def employee_deactivate(request, pk):
    employee = get_object_or_404(CustomUser, id=pk)
    if request.method == 'POST':
        form = EmployeeStatusForm(request.POST, instance=employee)
        if form.is_valid():
            status = form.cleaned_data['status']
            employee.status = status
            employee.is_active = status not in ['INACTIVE', 'TERMINATED']
            employee.save()
            messages.success(request, f'Statut de {employee.get_full_name()} mis à jour.')
            return redirect('accounts:employee_list')
    else:
        form = EmployeeStatusForm(instance=employee)
    return render(request, 'accounts/employee_deactivate.html', {'form': form, 'employee': employee})


@login_required
@user_passes_test(is_admin)
def employee_detail(request, pk):
    employee = get_object_or_404(CustomUser, id=pk)
    return render(request, 'accounts/employee_detail.html', {'employee': employee})


@login_required
@user_passes_test(is_manager_or_admin)
def my_team(request):
    if request.user.role == 'ADMIN':
        employees = CustomUser.objects.filter(role='EMPLOYEE').order_by('first_name', 'last_name')
    else:
        employees = CustomUser.objects.filter(manager=request.user).order_by('first_name', 'last_name')
    return render(request, 'accounts/my_team.html', {
        'employees': employees,
        'is_manager': request.user.role == 'MANAGER',
    })


@login_required
def my_profile(request):
    return render(request, 'accounts/my_profile.html', {'employee': request.user})


# ============ CONTRACTS ============

@login_required
@user_passes_test(is_admin)
def contract_create(request, employee_id):
    employee = get_object_or_404(CustomUser, id=employee_id)
    existing_contract = Contract.objects.filter(employee=employee).first()
    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.employee = employee
            contract.save()
            messages.success(request, f'Contrat ajouté pour {employee.get_full_name()}')
            return redirect('accounts:employee_detail', pk=employee.id)
    else:
        form = ContractForm()
    return render(request, 'accounts/contract_form.html', {
        'form': form, 'employee': employee, 'existing_contract': existing_contract
    })


@login_required
@user_passes_test(is_admin)
def contract_edit(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES, instance=contract)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contrat modifié avec succès')
            return redirect('accounts:employee_detail', pk=contract.employee.id)
    else:
        form = ContractForm(instance=contract)
    return render(request, 'accounts/contract_form.html', {'form': form, 'contract': contract})


@login_required
@user_passes_test(is_admin)
def contract_detail(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    return render(request, 'accounts/contract_detail.html', {'contract': contract})


# ============ PAYROLL ============

def calculate_absence_deduction(employee, daily_rate):
    month = timezone.now().month
    year = timezone.now().year
    absences = LeaveRequest.objects.filter(
        employee=employee, status='APPROVED',
        start_date__month=month, start_date__year=year
    )
    total_days = sum((l.end_date - l.start_date).days + 1 for l in absences)
    return total_days * daily_rate


@login_required
@user_passes_test(is_admin)
def generate_payslip_test(request, employee_id):
    employee = get_object_or_404(CustomUser, id=employee_id)
    month = timezone.now().month
    year = timezone.now().year

    base_salary = employee.salary or Decimal('1000')
    daily_rate = base_salary / 30

    # FIXED: added start_date__month=month
    approved_leaves = LeaveRequest.objects.filter(
        employee=employee,
        status='APPROVED',
        start_date__year=year,
        start_date__month=month,
    )
    absence_days = sum((l.end_date - l.start_date).days + 1 for l in approved_leaves)
    deduction = Decimal(absence_days) * daily_rate
    net_salary = base_salary - deduction

    payslip = Payslip.objects.filter(employee=employee, month=month, year=year).first()
    if payslip is None:
        payslip = Payslip.objects.create(
            employee=employee,
            month=month,
            year=year,
            base_salary=base_salary,
            bonus=Decimal('0'),
            deduction=deduction,
            net_salary=net_salary,
            is_finalized=False,
        )
        try:
            from datetime import date as d
            month_name = d(year, month, 1).strftime('%B %Y')
            send_mail(
                subject=f'Votre fiche de paie {month_name} est disponible',
                message=(
                    f'Bonjour {employee.get_full_name()},\n\n'
                    f'Votre fiche de paie pour {month_name} a été générée.\n\n'
                    f'Salaire de base : {base_salary} TND\n'
                    f'Déductions : {deduction} TND\n'
                    f'Salaire net : {net_salary} TND\n\n'
                    f'Connectez-vous pour la consulter.\n\nCordialement,\nService RH'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[employee.email],
                fail_silently=True,
            )
        except Exception:
            pass

    return render(request, 'accounts/payslip_detail.html', {'payslip': payslip, 'employee': employee})


@login_required
def employee_payslips(request, employee_id):
    employee = get_object_or_404(CustomUser, id=employee_id)
    payslips = Payslip.objects.filter(employee=employee).order_by('-year', '-month')
    return render(request, 'accounts/employee_payslips.html', {'employee': employee, 'payslips': payslips})


@login_required
@user_passes_test(is_admin)
def payroll_dashboard(request):
    employees = CustomUser.objects.filter(role='EMPLOYEE')
    month = timezone.now().month
    year = timezone.now().year
    data = []
    for emp in employees:
        payslip = Payslip.objects.filter(employee=emp, month=month, year=year).first()
        data.append({'employee': emp, 'payslip': payslip, 'generated': payslip is not None})
    return render(request, 'accounts/payroll_dashboard.html', {'data': data, 'month': month, 'year': year})


@login_required
@user_passes_test(is_admin)
def edit_payslip(request, payslip_id):
    payslip = get_object_or_404(Payslip, id=payslip_id)
    if request.method == 'POST':
        was_finalized = payslip.is_finalized
        payslip.bonus = Decimal(request.POST.get('bonus', payslip.bonus))
        payslip.deduction = Decimal(request.POST.get('deduction', payslip.deduction))
        payslip.net_salary = payslip.base_salary + payslip.bonus - payslip.deduction
        payslip.is_finalized = 'is_finalized' in request.POST
        payslip.save()

        if not was_finalized and payslip.is_finalized:
            try:
                from datetime import date as d
                month_name = d(payslip.year, payslip.month, 1).strftime('%B %Y')
                send_mail(
                    subject=f'Votre fiche de paie {month_name} est finalisée',
                    message=(
                        f'Bonjour {payslip.employee.get_full_name()},\n\n'
                        f'Votre fiche de paie pour {month_name} est finalisée.\n\n'
                        f'Salaire de base : {payslip.base_salary} TND\n'
                        f'Prime : {payslip.bonus} TND\n'
                        f'Déductions : {payslip.deduction} TND\n'
                        f'Salaire net : {payslip.net_salary} TND\n\n'
                        f'Connectez-vous pour la télécharger.\n\nCordialement,\nService RH'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[payslip.employee.email],
                    fail_silently=True,
                )
            except Exception:
                pass

        return redirect('accounts:payroll_dashboard')
    return render(request, 'accounts/edit_payslip.html', {'payslip': payslip})

@login_required
def payslip_pdf(request, payslip_id):
    payslip = get_object_or_404(Payslip, id=payslip_id)
    if not (request.user.role == 'ADMIN' or payslip.employee == request.user):
        return HttpResponseForbidden()
    template = get_template('accounts/payslip_pdf.html')
    html = template.render({'payslip': payslip})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="payslip_{payslip.month}_{payslip.year}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response

@login_required
def my_payslips(request):
    payslips = Payslip.objects.filter(employee=request.user).order_by('-year', '-month')
    return render(request, 'accounts/my_payslips.html', {'payslips': payslips})

@login_required
def payslip_detail(request, payslip_id):
    payslip = get_object_or_404(Payslip, id=payslip_id)
    if not (request.user.role == 'ADMIN' or payslip.employee == request.user):
        return HttpResponseForbidden()
    return render(request, 'accounts/payslip_detail.html', {'payslip': payslip})