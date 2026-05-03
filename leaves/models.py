from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class LeaveRequest(models.Model):
    # Types de congés possibles
    LEAVE_TYPES = [
        ('PAID', 'Congé payé'),
        ('RTT', 'RTT'),
        ('SICK', 'Maladie'),
        ('UNPAID', 'Congé sans solde'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('APPROVED', 'Approuvé'),
        ('REJECTED', 'Refusé'),
        ('CANCELLED', 'Annulé'),
    ]
    
    # Liens vers l'employé (utilisateur)
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    
    # Dates du congé
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Type et statut
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPES, default='PAID')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    # Informations supplémentaires
    reason = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='leave_certificates/', blank=True, null=True)
    
    # Pour le suivi
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves'
    )
    approval_comment = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.employee.username} - {self.start_date} to {self.end_date}"
    
    @property
    def days_requested(self):
        # Calcule le nombre de jours demandés
        delta = self.end_date - self.start_date
        return delta.days + 1
    
    class Meta:
        ordering = ['-created_at']


class LeaveBalance(models.Model):
    # Solde de congés par employé et par année
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leave_balances'
    )
    year = models.IntegerField()
    total_days = models.IntegerField(default=25)  # 25 jours par défaut
    taken_days = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['employee', 'year']
    
    @property
    def remaining_days(self):
        return self.total_days - self.taken_days
    
    def __str__(self):
        return f"{self.employee.username} - {self.year}: {self.remaining_days} restants"