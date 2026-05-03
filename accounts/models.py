from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
import uuid
# Manager personnalisé pour CustomUser
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'adresse email est obligatoire')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superuser doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superuser doit avoir is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    # Supprimer username
    username = None
    
    # Choix des rôles
    ROLE_CHOICES = [
        ('ADMIN', 'Admin RH'),
        ('MANAGER', 'Manager'),
        ('EMPLOYEE', 'Employé'),
    ]
    
    # Statut de l'employé
    STATUS_CHOICES = [
        ('ACTIVE', 'Actif'),
        ('INACTIVE', 'Inactif'),
        ('ON_LEAVE', 'En congé'),
        ('TERMINATED', 'Licencié'),
    ]
    
    # Champs existants
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    
    # Nouveaux champs pour la gestion des employés
    employee_id = models.CharField(max_length=20, unique=False, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True)  # Poste
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='team_members')
    contract_type = models.CharField(max_length=50, blank=True)  # CDI, CDD, Stage, etc.
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = CustomUserManager()
    
    def save(self, *args, **kwargs):
        # Générer un ID employé automatiquement si non fourni
        if not self.employee_id or self.employee_id == '':
            # Utiliser l'ID auto-incrémenté après sauvegarde
            if not self.pk:
                super().save(*args, **kwargs)
            self.employee_id = f"EMP{self.pk:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def get_status_display_fr(self):
        status_map = {
            'ACTIVE': 'Actif',
            'INACTIVE': 'Inactif',
            'ON_LEAVE': 'En congé',
            'TERMINATED': 'Licencié',
        }
        return status_map.get(self.status, self.status)

class Contract(models.Model):
    CONTRACT_TYPES = [
        ('CDI', 'CDI - Contrat à Durée Indéterminée'),
        ('CDD', 'CDD - Contrat à Durée Déterminée'),
        ('INTERIM', 'Intérim'),
        ('STAGE', 'Stage'),
        ('APPRENTISSAGE', 'Apprentissage'),
        ('FREELANCE', 'Freelance'),
    ]
    
    employee = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='contract')
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    probation_end_date = models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    salary_currency = models.CharField(max_length=3, default='EUR')
    working_hours = models.DecimalField(max_digits=5, decimal_places=2, default=35.00)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    job_description = models.TextField(blank=True)
    contract_file = models.FileField(upload_to='contracts/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.get_contract_type_display()}"
    
    def is_on_probation(self):
        if self.probation_end_date:
            return date.today() <= self.probation_end_date
        return False

class Payslip(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payslips')

    month = models.IntegerField()   # 1-12
    year = models.IntegerField()

    base_salary = models.DecimalField(max_digits=10, decimal_places=2)

    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    net_salary = models.DecimalField(max_digits=10, decimal_places=2)

    is_finalized = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'month', 'year')

    def __str__(self):
        return f"{self.employee.email} - {self.month}/{self.year}"