from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views import View

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

from django.urls import reverse_lazy
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from .models import Quest, Skill, Boss, PlayerProfile, Note, Item, QuestItem
from .forms import QuestForm, NoteForm, QuestFilterForm, SkillForm, BossForm
from .mixins import OwnerQuerysetMixin, QuestOwnerMixin, XPAwardMixin



class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        PlayerProfile.objects.create(user=self.object)
        Skill.objects.create(user=self.object, name='Python', color='#f59e0b')
        Skill.objects.create(user=self.object, name='Англійська', color='#6366f1')
        Skill.objects.create(user=self.object, name='Математика', color='#ef4444')
        login(self.request, self.object)
        return response




class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['skills'] = Skill.objects.filter(user=user)
        context['active_quests'] = (
            Quest.objects.filter(user=user, status__in=['pending', 'in_progress'])
            .select_related('skill').order_by('deadline')[:5]
        )
        context['upcoming_bosses'] = (
            Boss.objects.filter(user=user, status='preparing')
            .select_related('skill').order_by('deadline')[:3]
        )
        context['recent_completed'] = (
            Quest.objects.filter(user=user, status='completed')
            .order_by('-completed_at')[:5]
        )

        profile, _ = PlayerProfile.objects.get_or_create(user=user)
        profile.update_level()
        context['profile'] = profile

        return context




class QuestListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Quest
    template_name = 'quests/quest_list.html'
    context_object_name = 'quests'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('skill')
        form = QuestFilterForm(self.request.GET or None, user=self.request.user)
        if form.is_valid():
            if status := form.cleaned_data.get('status'):
                queryset = queryset.filter(status=status)
            if priority := form.cleaned_data.get('priority'):
                queryset = queryset.filter(priority=priority)
            if skill := form.cleaned_data.get('skill'):
                queryset = queryset.filter(skill=skill)
            if search := form.cleaned_data.get('search'):
                queryset = queryset.filter(title__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = QuestFilterForm(
            self.request.GET or None, user=self.request.user,
        )
        return context


class QuestDetailView(LoginRequiredMixin, QuestOwnerMixin, DetailView):
    model = Quest
    template_name = 'quests/quest_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notes'] = self.object.notes.select_related('user').all()
        context['note_form'] = NoteForm()

        profile = self.request.user.playerprofile
        all_items = Item.objects.all()
        context['available_items'] = [item for item in all_items if item.is_unlocked_for(profile)]
        context['quest_items'] = self.object.quest_items.select_related('item').all()

        return context


class QuestCreateView(LoginRequiredMixin, CreateView):
    model = Quest
    form_class = QuestForm
    template_name = 'quests/quest_form.html'
    success_url = reverse_lazy('quest_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        priority_xp = {'low': 10, 'medium': 25, 'high': 50, 'critical': 100}
        form.instance.xp_reward = priority_xp.get(form.instance.priority, 25)
        return super().form_valid(form)


class QuestUpdateView(LoginRequiredMixin, QuestOwnerMixin, UpdateView):
    model = Quest
    form_class = QuestForm
    template_name = 'quests/quest_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        priority_xp = {'low': 10, 'medium': 25, 'high': 50, 'critical': 100}
        form.instance.xp_reward = priority_xp.get(form.instance.priority, 25)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('quest_detail', kwargs={'pk': self.object.pk})


class QuestDeleteView(LoginRequiredMixin, QuestOwnerMixin, DeleteView):
    model = Quest
    template_name = 'quests/quest_confirm_delete.html'
    success_url = reverse_lazy('quest_list')




class CompleteQuestView(LoginRequiredMixin, XPAwardMixin, View):
    def post(self, request, pk):
        quest = get_object_or_404(Quest, pk=pk, user=request.user)
        if quest.status == 'completed':
            return redirect('quest_detail', pk=pk)
        self.award_xp(quest)
        quest.status = 'completed'
        quest.completed_at = timezone.now()
        quest.save()
        return redirect('quest_detail', pk=pk)




class AddNoteView(LoginRequiredMixin, View):
    def post(self, request, quest_pk):
        quest = get_object_or_404(Quest, pk=quest_pk, user=request.user)
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.quest = quest
            note.user = request.user
            note.save()
        return redirect('quest_detail', pk=quest_pk)


class DeleteNoteView(LoginRequiredMixin, View):
    def post(self, request, quest_pk, pk):
        note = get_object_or_404(Note, pk=pk)
        if note.user != request.user:
            raise PermissionDenied
        quest_pk = note.quest.pk
        note.delete()
        return redirect('quest_detail', pk=quest_pk)




class SkillListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Skill
    template_name = 'skills/skill_list.html'
    context_object_name = 'skills'


class SkillDetailView(LoginRequiredMixin, OwnerQuerysetMixin, DetailView):
    model = Skill
    template_name = 'skills/skill_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quests'] = (
            self.object.quests.order_by('-created_at').select_related('user')[:10]
        )
        context['completed_count'] = self.object.quests.filter(status='completed').count()
        context['bosses'] = self.object.bosses.filter(status='preparing').order_by('deadline')
        return context


class SkillCreateView(LoginRequiredMixin, CreateView):
    model = Skill
    form_class = SkillForm
    template_name = 'skills/skill_form.html'
    success_url = reverse_lazy('skill_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class SkillDeleteView(LoginRequiredMixin, OwnerQuerysetMixin, DeleteView):
    model = Skill
    template_name = 'skills/skill_confirm_delete.html'
    success_url = reverse_lazy('skill_list')




class BossListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Boss
    template_name = 'bosses/boss_list.html'
    context_object_name = 'bosses'


class BossCreateView(LoginRequiredMixin, CreateView):
    model = Boss
    form_class = BossForm
    template_name = 'bosses/boss_form.html'
    success_url = reverse_lazy('boss_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class BossUpdateView(LoginRequiredMixin, OwnerQuerysetMixin, UpdateView):
    model = Boss
    form_class = BossForm
    template_name = 'bosses/boss_form.html'
    success_url = reverse_lazy('boss_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class BossDeleteView(LoginRequiredMixin, OwnerQuerysetMixin, DeleteView):
    model = Boss
    template_name = 'bosses/boss_confirm_delete.html'
    success_url = reverse_lazy('boss_list')


class BossFightView(LoginRequiredMixin, View):
    def post(self, request, pk):
        boss = get_object_or_404(Boss, pk=pk, user=request.user)

        if not boss.is_ready:
            return redirect('boss_list')

        if boss.status == 'defeated':
            return redirect('boss_list')

        profile = request.user.playerprofile
        profile.total_xp += boss.reward_xp
        profile.update_level()

        boss.status = 'defeated'
        boss.save()

        return redirect('boss_list')




class InventoryView(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'inventory/inventory.html'
    context_object_name = 'items'

    def get_queryset(self):
        return Item.objects.all().order_by('unlock_level', 'item_type')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.playerprofile
        context['player_level'] = profile.player_level
        context['unlocked_items'] = [item for item in context['items'] if item.is_unlocked_for(profile)]
        context['locked_items'] = [item for item in context['items'] if not item.is_unlocked_for(profile)]
        return context


class AddItemToQuestView(LoginRequiredMixin, View):
    def post(self, request, quest_pk, item_pk):
        quest = get_object_or_404(Quest, pk=quest_pk, user=request.user)
        item = get_object_or_404(Item, pk=item_pk)

        profile = request.user.playerprofile
        if not item.is_unlocked_for(profile):
            raise PermissionDenied

        QuestItem.objects.get_or_create(quest=quest, item=item)
        return redirect('quest_detail', pk=quest_pk)


class RemoveItemFromQuestView(LoginRequiredMixin, View):
    def post(self, request, quest_pk, item_pk):
        quest = get_object_or_404(Quest, pk=quest_pk, user=request.user)
        item = get_object_or_404(Item, pk=item_pk)

        QuestItem.objects.filter(quest=quest, item=item).delete()
        return redirect('quest_detail', pk=quest_pk)


class HelpView(LoginRequiredMixin, TemplateView):
    template_name = 'help.html'