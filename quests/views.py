from django.shortcuts import render

from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from mixins import PlayerRequiredMixin

from .models import Quest
from .forms import QuestForm, CommentForm


class QuestListView(PlayerRequiredMixin, ListView):
    model = Quest
    template_name = 'quests/quest_list.html'
    context_object_name = 'quests'

    def get_queryset(self):
        qs = Quest.objects.filter(player=self.request.user.playerprofile)
        status = self.request.GET.get('status')
        skill = self.request.GET.get('skill')
        difficulty = self.request.GET.get('difficulty')
        if status:
            qs = qs.filter(status=status)
        if skill:
            qs = qs.filter(skill_id=skill)
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from skills.models import Skill
        context['skills'] = Skill.objects.filter(player=self.request.user.playerprofile)
        context['difficulties'] = Quest.DIFFICULTY
        context['statuses'] = Quest.STATUS
        context['filter_status'] = self.request.GET.get('status', '')
        context['filter_skill'] = self.request.GET.get('skill', '')
        context['filter_difficulty'] = self.request.GET.get('difficulty', '')
        return context


class QuestDetailView(PlayerRequiredMixin, DetailView):
    model = Quest
    template_name = 'quests/quest_detail.html'
    context_object_name = 'quest'

    def get_queryset(self):
        return Quest.objects.filter(player=self.request.user.playerprofile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context


class QuestCreateView(PlayerRequiredMixin, CreateView):
    model = Quest
    form_class = QuestForm
    template_name = 'quests/quest_create.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        from skills.models import Skill
        from campaigns.models import Campaign
        form.fields['skill'].queryset = Skill.objects.filter(player=self.request.user.playerprofile)
        form.fields['campaign'].queryset = Campaign.objects.filter(player=self.request.user.playerprofile)
        return form

    def form_valid(self, form):
        form.instance.player = self.request.user.playerprofile
        return super().form_valid(form)


class QuestDeleteView(DeleteView):
    model = Quest
    template_name = 'quests/quest_confirm_delete.html'
