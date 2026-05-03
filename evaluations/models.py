from django.db import models
from accounts.models import CustomUser
from django.utils import timezone

class EvaluationCampaign(models.Model):
    title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_campaigns')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Evaluation(models.Model):
    STATUS_CHOICES = [('draft', 'Brouillon'), ('submitted', 'Soumis'), ('validated', 'Validé')]

    campaign = models.ForeignKey(EvaluationCampaign, on_delete=models.CASCADE)
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='evaluations')
    manager = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='evaluations_given'
    )
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    comments = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_self_evaluation = models.BooleanField(default=False)

    class Meta:
        unique_together = ('campaign', 'employee', 'is_self_evaluation')

    def __str__(self):
        return f"{self.employee} - {self.campaign}"

class EvaluationCriterion(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='criteria')
    name = models.CharField(max_length=200)          # ex: "Qualité du travail"
    description = models.TextField(blank=True)
    weight = models.IntegerField(default=1)          # Pondération
    score = models.IntegerField(null=True, blank=True)  # Note / 5 ou /10

class Goal(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    progress = models.IntegerField(default=0)  # Pourcentage
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='goals_created')