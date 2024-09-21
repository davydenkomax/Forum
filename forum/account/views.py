from typing import Any
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import Http404, HttpRequest, HttpResponse
from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView, View
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RegistrationForm, ProfileUpdateForm, UserUpdateForm
from .models import Profile
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from content.models import Message, Subject, SubjectView
from redis import Redis
from django.conf import settings
from django.core.cache import cache

r = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

class RegisterView(CreateView):
    template_name = 'register/register.html'
    success_url = reverse_lazy('login')
    form_class = RegistrationForm

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        cd = form.cleaned_data
        new_user = form.save(commit=False)

        new_user.set_password(cd['password1'])
        new_user.save()
        Profile.objects.create(user=new_user)

        return super().form_valid(form)
    
class ProfileUserUpdateView(LoginRequiredMixin, View):
    template_name = 'update/update_profile_user.html'
    first_form = UserUpdateForm
    second_form = ProfileUpdateForm
    success_url = reverse_lazy('content:section_list')

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        user_form = self.first_form(instance=request.user)
        profile_form = self.second_form(instance=request.user.profile)

        return self.render_to_response(self.get_context_data(
            user_form=user_form,
            profile_form=profile_form
        ))
    
    def post(self, request, *args, **kwargs):
        user_form = self.first_form(
            data=request.POST,
            instance=request.user,
        )
        profile_form = self.second_form(
            data=request.POST,
            instance=request.user.profile,
            files=request.FILES
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            return redirect(self.success_url)

        return self.render_to_response(self.get_context_data(
            user_form=user_form,
            profile_form=profile_form
        ))
    
class HistoryMessagesListView(LoginRequiredMixin, ListView):
    template_name = 'profile/history_messages.html'
    model = Message
    context_object_name = 'messages'

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(
            author=self.request.user,
        ).order_by('-created')
    
class SubjectsByAuthorListView(LoginRequiredMixin, ListView):
    template_name = 'profile/subjects_by_author.html'
    model = Subject
    context_object_name = 'subjects'

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(
            author=self.request.user,
            active=True
        ).order_by('-created')
    
class StatisticsSubject(LoginRequiredMixin, ListView):
    template_name = 'statistics/statistics_subject.html'
    model = SubjectView
    
    def get_total_views(self):
        total_views = r.get(f'subject:{self.kwargs["subject_id"]}:views')
        return int(total_views) if total_views else 0
    
    def get_subject(self):
        return get_object_or_404(
            Subject,
            id=self.kwargs['subject_id']
        )

    def has_permission(self):
        subject = self.get_subject()
        if subject.author == self.request.user:
            return True
        return False

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['subject'] = self.get_subject()

        context['total_views'] = self.get_total_views()

        subject_views = cache.get(f'subject_views:{self.kwargs["subject_id"]}')
        if not subject_views:
            subject_views = self.get_queryset()
            cache.set(f'subject_views:{self.kwargs["subject_id"]}', subject_views, 60 * 60 * 24)

        if subject_views:
            
            context['views_data'] = {
                'labels': [obj.date.strftime("%Y.%m.%d") for obj in subject_views],
                'values': [obj.views for obj in subject_views],
            }

            return context

        context['views_data'] = None
        return context

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(
            subject_id=self.kwargs['subject_id'],
            subject__slug=self.kwargs['subject_slug']
        )
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not self.has_permission():
            raise Http404('У вас нет разрешения')
        return super().get(request, *args, **kwargs)