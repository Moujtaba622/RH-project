from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('leaves/', include('leaves.urls')),
    path('evaluations/', include('evaluations.urls', namespace='evaluations')),
    path('', RedirectView.as_view(url='/accounts/login/')),  # ← ADD THIS
]