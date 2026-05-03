from django.contrib import admin
from .models import EvaluationCampaign, Evaluation, EvaluationCriterion, Goal

admin.site.register(EvaluationCampaign)
admin.site.register(Evaluation)
admin.site.register(EvaluationCriterion)
admin.site.register(Goal)