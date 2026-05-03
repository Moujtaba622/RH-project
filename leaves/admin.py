from django.contrib import admin
from .models import LeaveRequest, LeaveBalance

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'start_date', 'end_date', 'leave_type', 'status']
    list_filter = ['status', 'leave_type']
    search_fields = ['employee__username', 'employee__email']

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'year', 'total_days', 'taken_days', 'remaining_days']
    list_filter = ['year']