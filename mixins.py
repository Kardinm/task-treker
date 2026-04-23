from django.shortcuts import redirect
from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin

class StaminaRequiredMixin:
    stamina_cost = 10
    def dispatch(self, request, *args, **kwargs):
        if request.user.playerprofile.stamina < self.stamina_cost:
            messages.error(request, "Недостатньо енергії!")
            return redirect('quest_list')
        return super().dispatch(request, *args, **kwargs)
    def deduct_stamina(self, request):
        request.user.playerprofile.stamina -= self.stamina_cost
        request.user.playerprofile.save()

class PlayerRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'playerprofile'):
            return redirect('profile_create')
        return super().dispatch(request, *args, **kwargs)