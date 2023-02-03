from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import CreationForm, UserEditForm, ProfileEditForm
from users.models import Profile


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        Profile.objects.create(user=user)
        return super().form_valid(form)


class ProfileEdit(UpdateView, LoginRequiredMixin):
    model = Profile
    form_class = ProfileEditForm
    template_name = 'users/profile_edit.html'
    pk_url_kwarg = 'profile_id'

    def get_context_data(self, **kwargs):
        profile_form = ProfileEditForm(instance=self.request.user.profile)
        user_form = UserEditForm(instance=self.request.user)
        context = {
            'profile_form': profile_form,
            'user_form': user_form,
        }
        return super().get_context_data(**context)

    def post(self, request, *args, **kwargs):
        profile_form = ProfileEditForm(
            request.POST or None,
            files=request.FILES or None,
            instance=request.user.profile,
        )
        user_form = UserEditForm(request.POST or None, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            user_form.save()
            return self.form_valid(profile_form)
        else:
            return self.form_invalid(profile_form)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
