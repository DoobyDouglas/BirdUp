from users.models import Profile


class DataMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        profile = Profile.objects.get(user=self.request.user)
        context['profile'] = profile
        return context
