from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import LeaveRequest, LeaveBalance

@login_required
def request_leave(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        leave_type = request.POST.get('leave_type')
        reason = request.POST.get('reason')
        
        # Créer la demande
        leave_request = LeaveRequest.objects.create(
            employee=request.user,
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
            reason=reason,
            status='PENDING'
        )
        messages.success(request, 'Votre demande de congé a été envoyée avec succès !')
        return redirect('my_requests')
    
    return render(request, 'leaves/request_leave.html')

@login_required
def my_requests(request):
    requests = LeaveRequest.objects.filter(employee=request.user).order_by('-created_at')
    return render(request, 'leaves/my_requests.html', {'requests': requests})

@login_required
def leave_balance(request):
    try:
        balance = LeaveBalance.objects.get(employee=request.user, year=timezone.now().year)
    except LeaveBalance.DoesNotExist:
        balance = None
    return render(request, 'leaves/leave_balance.html', {'balance': balance})

@login_required
def pending_requests(request):
    # Seuls les managers et admins peuvent voir
    if not request.user.is_staff:
        messages.error(request, 'Vous n\'avez pas les droits pour accéder à cette page.')
        return redirect('accounts:dashboard')
    
    pending = LeaveRequest.objects.filter(status='PENDING').order_by('-created_at')
    return render(request, 'leaves/pending_requests.html', {'pending': pending})

@login_required
def approve_leave(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    if request.user.is_staff:
        leave_request.status = 'APPROVED'
        leave_request.approved_by = request.user
        leave_request.save()
        
        # Mettre à jour le solde
        balance = LeaveBalance.objects.get(employee=leave_request.employee, year=timezone.now().year)
        balance.taken_days += leave_request.days_requested
        balance.save()
        
        messages.success(request, f'Demande de {leave_request.employee.username} approuvée.')
    return redirect('pending_requests')

@login_required
def reject_leave(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    if request.user.is_staff:
        leave_request.status = 'REJECTED'
        leave_request.save()
        messages.success(request, f'Demande de {leave_request.employee.username} refusée.')
    return redirect('pending_requests')


from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from decimal import Decimal

from accounts.models import CustomUser, Contract, Payslip

def is_admin(user):
    return user.role == "ADMIN"


@login_required
@user_passes_test(is_admin)
def generate_payslip_test(request, employee_id):
    employee = get_object_or_404(CustomUser, id=employee_id)

    contract = get_object_or_404(Contract, employee=employee)

    # TEST VALUES (we will improve later)
    bonus = Decimal("100")
    deduction = Decimal("50")

    net_salary = contract.salary + bonus - deduction

    payslip = Payslip.objects.create(
        employee=employee,
        month=4,   # hardcoded for now (April test)
        year=2026,
        base_salary=contract.salary,
        bonus=bonus,
        deduction=deduction,
        net_salary=net_salary,
        is_finalized=True
    )

    messages.success(request, f"Payslip created for {employee.email}")

    return redirect('accounts:dashboard')