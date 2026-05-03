from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import CustomUser
from .models import EvaluationCampaign, Evaluation, EvaluationCriterion, Goal
from django.db import transaction

# ==================== MANAGER & ADMIN VIEWS ====================

@login_required
def campaign_list(request):
    campaigns = EvaluationCampaign.objects.all().order_by('-created_at')
    return render(request, 'evaluations/campaign_list.html', {'campaigns': campaigns})


@login_required
def campaign_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        EvaluationCampaign.objects.create(
            title=title,
            start_date=start_date,
            end_date=end_date,
            created_by=request.user
        )
        messages.success(request, "Campagne d'évaluation créée avec succès!")
        return redirect('evaluations:campaign_list')
    
    return render(request, 'evaluations/campaign_create.html')


@login_required
def evaluate_employee(request, employee_id):
    employee = get_object_or_404(CustomUser, id=employee_id)
    
    # For now, use the latest active campaign
    campaign = EvaluationCampaign.objects.filter(is_active=True).first()
    if not campaign:
        messages.error(request, "Aucune campagne active trouvée.")
        return redirect('evaluations:campaign_list')

    if request.method == 'POST':
        with transaction.atomic():
            evaluation = Evaluation.objects.create(
                campaign=campaign,
                employee=employee,
                manager=request.user,
                comments=request.POST.get('comments'),
                status='submitted'
            )
            
            # Example criteria (you can improve this later)
            criteria_names = ["Qualité du travail", "Productivité", "Esprit d'équipe", "Ponctualité"]
            for name in criteria_names:
                score = request.POST.get(f'score_{name}')
                if score:
                    EvaluationCriterion.objects.create(
                        evaluation=evaluation,
                        name=name,
                        score=int(score)
                    )
            
            messages.success(request, f"Évaluation de {employee.get_full_name()} enregistrée.")
            return redirect('evaluations:my_evaluations')

    return render(request, 'evaluations/evaluate_employee.html', {
        'employee': employee,
        'campaign': campaign
    })


@login_required
def my_evaluations(request):
    evaluations = Evaluation.objects.filter(employee=request.user)
    return render(request, 'evaluations/my_evaluations.html', {'evaluations': evaluations})


@login_required
def evaluation_detail(request, pk):
    evaluation = get_object_or_404(Evaluation, pk=pk)
    return render(request, 'evaluations/evaluation_detail.html', {'evaluation': evaluation})


# ==================== GOALS ====================

@login_required
def goal_list(request):
    goals = Goal.objects.filter(employee=request.user)
    return render(request, 'evaluations/goal_list.html', {'goals': goals})


@login_required
def goal_create(request, employee_id):
    employee = get_object_or_404(CustomUser, id=employee_id)
    if request.method == 'POST':
        Goal.objects.create(
            employee=employee,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            due_date=request.POST.get('due_date'),
            created_by=request.user
        )
        messages.success(request, "Objectif ajouté avec succès!")
        return redirect('evaluations:goal_list')
    
    return render(request, 'evaluations/goal_create.html', {'employee': employee})


# ==================== SELF-EVALUATION (EMPLOYEE) ====================

@login_required
def self_evaluate(request):
    """En tant qu'Employé, je veux faire une auto-évaluation"""
    campaign = EvaluationCampaign.objects.filter(is_active=True).first()
    if not campaign:
        messages.error(request, "Aucune campagne d'évaluation active.")
        return redirect('evaluations:my_evaluations')

    # Check if employee already submitted a self-evaluation for this campaign
    existing = Evaluation.objects.filter(
        campaign=campaign,
        employee=request.user,
        is_self_evaluation=True
    ).first()
    if existing:
        messages.info(request, "Vous avez déjà soumis une auto-évaluation pour cette campagne.")
        return redirect('evaluations:my_evaluations')

    if request.method == 'POST':
        with transaction.atomic():
            evaluation = Evaluation.objects.create(
                campaign=campaign,
                employee=request.user,
                manager=None,
                comments=request.POST.get('comments'),
                status='submitted',
                is_self_evaluation=True
            )
            criteria_names = ["Qualité du travail", "Productivité", "Esprit d'équipe", "Ponctualité"]
            for name in criteria_names:
                score = request.POST.get(f'score_{name}')
                if score:
                    EvaluationCriterion.objects.create(
                        evaluation=evaluation,
                        name=name,
                        score=int(score)
                    )
            messages.success(request, "Auto-évaluation soumise avec succès!")
            return redirect('evaluations:my_evaluations')

    criteria_names = ["Qualité du travail", "Productivité", "Esprit d'équipe", "Ponctualité"]
    return render(request, 'evaluations/self_evaluate.html', {
        'campaign': campaign,
        'criteria_names': criteria_names,
    })


# ==================== ADMIN VIEW ====================

@login_required
def all_evaluations(request):
    """En tant qu'Admin RH, je veux consulter toutes les évaluations"""
    if request.user.role not in ['ADMIN', 'MANAGER']:
        messages.error(request, "Accès non autorisé.")
        return redirect('accounts:dashboard')

    evaluations = Evaluation.objects.all().select_related(
        'employee', 'manager', 'campaign'
    ).order_by('-created_at')

    # Filters
    campaign_filter = request.GET.get('campaign', '')
    employee_filter = request.GET.get('employee', '')
    type_filter = request.GET.get('type', '')  # self or manager

    if campaign_filter:
        evaluations = evaluations.filter(campaign_id=campaign_filter)
    if employee_filter:
        evaluations = evaluations.filter(
            Q(employee__first_name__icontains=employee_filter) |
            Q(employee__last_name__icontains=employee_filter)
        )
    if type_filter == 'self':
        evaluations = evaluations.filter(is_self_evaluation=True)
    elif type_filter == 'manager':
        evaluations = evaluations.filter(is_self_evaluation=False)

    campaigns = EvaluationCampaign.objects.all()

    return render(request, 'evaluations/all_evaluations.html', {
        'evaluations': evaluations,
        'campaigns': campaigns,
        'campaign_filter': campaign_filter,
        'employee_filter': employee_filter,
        'type_filter': type_filter,
    })

@login_required
def campaign_detail(request, pk):
    campaign = get_object_or_404(EvaluationCampaign, pk=pk)
    # Get all employees the manager can evaluate
    if request.user.role == 'MANAGER':
        employees = CustomUser.objects.filter(manager=request.user, role='EMPLOYEE')
    else:
        employees = CustomUser.objects.filter(role='EMPLOYEE')
    
    # Get existing evaluations for this campaign
    evaluations = Evaluation.objects.filter(
        campaign=campaign
    ).select_related('employee', 'manager')
    
    # Mark which employees already have evaluations
    evaluated_ids = evaluations.values_list('employee_id', flat=True)
    
    return render(request, 'evaluations/campaign_detail.html', {
        'campaign': campaign,
        'employees': employees,
        'evaluations': evaluations,
        'evaluated_ids': evaluated_ids,
    })

@login_required
def evaluate_employee(request, employee_id):
    employee = get_object_or_404(CustomUser, id=employee_id)
    campaign = EvaluationCampaign.objects.filter(is_active=True).first()
    if not campaign:
        messages.error(request, "Aucune campagne active trouvée.")
        return redirect('evaluations:campaign_list')

    criteria_names = ["Qualité du travail", "Productivité", "Esprit d'équipe", "Ponctualité", "Communication"]

    if request.method == 'POST':
        with transaction.atomic():
            evaluation = Evaluation.objects.create(
                campaign=campaign,
                employee=employee,
                manager=request.user,
                comments=request.POST.get('comments'),
                status='submitted'
            )
            for name in criteria_names:
                score = request.POST.get(f'score_{name}')
                if score:
                    EvaluationCriterion.objects.create(
                        evaluation=evaluation,
                        name=name,
                        score=int(score)
                    )
            messages.success(request, f"Évaluation de {employee.get_full_name()} enregistrée.")
            return redirect('evaluations:campaign_detail', pk=campaign.pk)

    return render(request, 'evaluations/evaluate_employee.html', {
        'employee': employee,
        'campaign': campaign,
        'criteria_names': criteria_names,
    })