from django.core.exceptions import PermissionDenied


class OwnerQuerysetMixin:
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class QuestOwnerMixin:
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        
        return obj


class XPAwardMixin:
    def award_xp(self, quest):
        xp_earned = quest.calculate_xp

        if quest.is_overdue and quest.penalty_xp > 0:
            xp_earned = max(0, xp_earned - quest.penalty_xp)

        quest.skill.add_xp(xp_earned)

        profile = self.request.user.playerprofile
        profile.total_xp += xp_earned
        profile.update_level()

        return xp_earned