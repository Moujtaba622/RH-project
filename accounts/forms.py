from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'role', 'phone', 'department', 
                  'position', 'contract_type', 'hire_date', 'salary', 'manager')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'w-full p-2 border rounded'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'w-full p-2 border rounded'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs.update({'class': 'w-full p-2 border rounded'})

class UserRoleForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={'class': 'w-full p-2 border rounded'})
        }

# Formulaire pour ajouter/modifier un employé (Admin seulement)
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'employee_id', 'email', 'first_name', 'last_name', 'role', 
            'department', 'position', 'phone', 'hire_date', 'contract_type',
            'salary', 'manager', 'status', 'address', 'emergency_contact',
            'emergency_phone', 'birth_date'
        ]
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border rounded'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border rounded'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'w-full p-2 border rounded'}),
            'employee_id': forms.TextInput(attrs={'class': 'w-full p-2 border rounded bg-gray-100', 'readonly': 'readonly'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'employee_id':
                self.fields[field].widget.attrs.update({'class': 'w-full p-2 border rounded'})
        
        # Limiter les managers aux utilisateurs avec rôle MANAGER ou ADMIN
        self.fields['manager'].queryset = CustomUser.objects.filter(role__in=['MANAGER', 'ADMIN'])
        self.fields['manager'].required = False

# Formulaire pour désactiver un employé
class EmployeeStatusForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'w-full p-2 border rounded'})
        }


from .models import Contract

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = [
            'contract_type', 'start_date', 'end_date', 'probation_end_date',
            'salary', 'working_hours', 'position', 'department', 
            'job_description', 'contract_file', 'is_active'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border rounded'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border rounded'}),
            'probation_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border rounded'}),
            'job_description': forms.Textarea(attrs={'rows': 4, 'class': 'w-full p-2 border rounded'}),
        }