from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views import View

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

from django.urls import reverse_lazy
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from .models import Quest, Skill, Boss, PlayerProfile, Note, Item
from .forms import QuestForm, NoteForm, QuestFilterForm
from .mixins import OwnerQuerysetMixin, QuestOwnerMixin, XPAwardMixin



class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        PlayerProfile.objects.create(user=self.object)
        Skill.objects.create(user=self.object, name='Python',    color='#f59e0b')
        Skill.objects.create(user=self.object, name='Англійська', color='#6366f1')
        Skill.objects.create(user=self.object, name='Математика', color='#ef4444')
        Item.objects.create(
            user=self.object, name='Pomodoro',
            item_type='focus',
            description='25 хвилин роботи → 5 хвилин перерви. Повтори 4 рази — потім велика пауза 20 хв.',
            effect_value=25, quantity=5,
        )
        Item.objects.create(
            user=self.object, name='Прогулянка',
            item_type='recovery',
            description='Вийди на 10–15 хвилин. Рух допомагає мозку.',
            effect_value=15, quantity=3,
        )
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
        context['items'] = Item.objects.filter(user=user, quantity__gt=0)[:4]

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
        return context





class BossListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    model = Boss
    template_name = 'bosses/boss_list.html'
    context_object_name = 'bosses'





class InventoryView(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'inventory/inventory.html'
    context_object_name = 'items'

    def get_queryset(self):
        return Item.objects.filter(user=self.request.user).order_by('item_type', 'name')


class UseItemView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk, user=request.user)
        item.use()
        return redirect('inventory')