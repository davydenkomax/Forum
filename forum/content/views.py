from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import FormView, DeleteView
from django.views.generic.base import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Section, Subject, Message, Content
from .forms import SubjectForm, TextForm
from django.forms import modelform_factory
from django.conf import settings
from django.apps import apps
from .tasks import task_send_mail
from django.core.cache import cache
import redis

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

# Create your views here.
class SectionListView(ListView):
    template_name = 'section/section_list.html'
    model = Section
    context_object_name = 'sections'

    def get_queryset(self) -> QuerySet[Any]:
        
        cache_section_list = cache.get('section_list')
        if cache_section_list:
            return cache_section_list
        
        section_list = super().get_queryset().filter(active=True)
        cache.set('section_list', section_list, 60 * 60)

        return section_list
    
class SubjectListView(ListView):
    model = Subject
    template_name = 'subject/subject_list.html'
    context_object_name = 'subjects'
    section = None

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:

        section_slug = self.kwargs['section_slug']
        self.section = get_object_or_404(
            Section,
            slug=section_slug
        )

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['section'] = self.section

        for subject in context['subjects']:
            subject.total_views = r.get(f'subject:{subject.id}:views')
            subject.total_views = int(subject.total_views) if subject.total_views else 0

        return context
    
    def get_queryset(self) -> QuerySet[Any]:

        cache_subject_list = cache.get(f'subject_list:{self.section.id}')
        if cache_subject_list:
            return cache_subject_list

        subject_list = super().get_queryset() \
            .filter(active=True, section__slug=self.kwargs['section_slug'])
        cache.set(f'subject_list:{self.section.id}', subject_list, 60 * 60)

        return subject_list
    
class MessageCreateView(LoginRequiredMixin, View):
    template_name = 'manage/create_message.html'
    subject_obj = None
    parent_message = None
    has_permission = True

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        if 'text_form' not in context:
            context['text_form'] = TextForm()
        if 'subject' not in context:
            context['subject'] = self.subject_obj
        if 'parent_message' not in context:
            context['parent_message'] = self.parent_message

        return context

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        subject_id = self.kwargs['subject_id']
        subject_slug = self.kwargs['subject_slug'] 
        
        self.subject_obj = get_object_or_404(
            Subject,
            id=subject_id,
            slug=subject_slug
        )

        parent_message_id = request.GET.get('id')
        if parent_message_id:
            self.parent_message = get_object_or_404(
                    Message,
                    id=parent_message_id
                )
            
            if self.parent_message.subject != self.subject_obj:
                self.has_permission = False

        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not self.has_permission:
            return redirect(self.subject_obj.get_absolute_url())
        return super().get(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:        

        if self.subject_obj:
            text_form = TextForm(request.POST)

            if text_form.is_valid():
                text_obj = text_form.save()

                if self.parent_message:
                    task_send_mail.delay(request.user.id, self.parent_message.id)

                message = Message.objects.create(
                    author=request.user,
                    subject=self.subject_obj,
                    parent_message=self.parent_message
                )
                Content.objects.create(
                    message=message,
                    item=text_obj
                )

                return redirect(self.subject_obj.get_absolute_url())
            
            return self.render_to_response(self.get_context_data(
                text_form=text_form,
                parent_message=self.parent_message
            ))
        
        return redirect('content:not_found')
    
class SubjectCreateView(LoginRequiredMixin, View):
    template_name = 'manage/create_subject.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        if 'subject_form' not in context:
            context['subject_form'] = SubjectForm()
        if 'text_form' not in context:
            context['text_form'] = TextForm()

        return context
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        
        subject_form = SubjectForm(request.POST)
        text_form = TextForm(request.POST)

        if subject_form.is_valid() and text_form.is_valid():
            text_obj = text_form.save()
            subject_obj = subject_form.save(commit=False)

            subject_obj.author = request.user
            subject_obj.save()
            
            message = Message.objects.create(
                author=request.user,
                subject=subject_obj,
            )     
            Content.objects.create(
                message=message,
                item=text_obj
            )

            
            return redirect(subject_obj.get_absolute_url())
        
        return self.render_to_response(self.get_context_data(
            subject_form=subject_form,
            text_form=text_form,
        ))
    
class MessageListView(ListView):
    template_name = 'message/list_message_by_subject.html'
    context_object_name = 'messages'
    model = Message

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        subject_id = self.kwargs['subject_id']
        r.incr(f'subject:{subject_id}:views')
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Any]:

        section_slug = self.kwargs['section_slug']
        subject_slug = self.kwargs['subject_slug']
        subject_id = self.kwargs['subject_id']

        cache_message_list = cache.get(f'message_list:{subject_id}:{subject_slug}')
        if cache_message_list:
            return cache_message_list

        message_list = super().get_queryset().filter(
            subject__section__slug=section_slug,
            subject_id=subject_id,
            subject__slug=subject_slug,
        )
        cache.set(f'message_list:{subject_id}:{subject_slug}', message_list, 60 * 60)

        return message_list
    
class ContentCreateUpdateView(LoginRequiredMixin, View):
    template_name = 'content/create_update_content.html'
    model = None
    message = None
    object = None
    has_permission = False

    def get_model(self, name_model):
        if name_model in ['text', 'image', 'video']:
            return apps.get_model(
                'content',
                model_name=name_model
            )
        
        return None
    
    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, fields='__all__')
        
        return Form(*args, **kwargs)
    
    def dispatch(self, request: HttpRequest, message_id, *args: Any, **kwargs: Any) -> HttpResponse:
        self.message = get_object_or_404(
            Message,
            id=message_id
        )
        
        name_model = request.GET.get('content')
        object_id = request.GET.get('id')
        if object_id:
            self.object = get_object_or_404(
                Content,
                id=object_id
            )

            if self.object.message.author == request.user \
                and self.object.content_type.model == name_model:
                self.has_permission = True

        self.model = self.get_model(name_model)

        if self.message.author == request.user and not self.object:
            self.has_permission = True
        
        if self.message.author != request.user and self.object:
            self.has_permission = False

        return super().dispatch(request, message_id, *args, **kwargs)
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not self.has_permission:
            return redirect(self.message.subject.get_absolute_url())
        
        form = self.get_form(
            self.model,
            instance = self.object.item if self.object else None
        )

        return self.render_to_response(self.get_context_data(
            form=form,
            object=self.object
        )) 
    
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = self.get_form(
            self.model, 
            instance=self.object.item if self.object else None,
            data=request.POST,
            files=request.FILES
        )

        if form.is_valid():
            obj = form.save()

            if not self.object:
                self.object = Content.objects.create(
                    message=self.message,
                    item=obj
                )
            else:
                self.object.save()

            return redirect(self.message.subject.get_absolute_url())
            
        return self.render_to_response(self.get_context_data(
            form=form,
            object=self.object
        ))
    
class ContentDeleteView(LoginRequiredMixin, DeleteView):
    model = Content
    template_name = 'manage/delete_content.html'
    pk_url_kwarg = 'content_id'
    object = None
    context_object_name = 'content'

    def has_permission(self):
        self.object = self.get_object()
        count_content = self.object.message.contents.count()

        if self.request.user == self.object.message.author and count_content > 1:
            return True
        return False    
    
    def get_success_url(self) -> str:
        return self.object.message.subject.get_absolute_url()

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if self.has_permission():
            return super().post(request, *args, **kwargs)
        pass
        return self.get_success_url()
    
class FindSubjectListView(ListView):
    template_name = 'manage/search_result.html'
    model = Subject
    context_object_name = 'subjects'
    search = None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['search'] = self.search

        for subject in context['subjects']:
            subject.total_views = r.get(f'subject:{subject.id}:views')
            subject.total_views = int(subject.total_views) if subject.total_views else 0

        return context

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        self.search = self.request.GET.get('search')

        if not self.search:
            return None

        return queryset.filter(name__icontains=self.search, active=True)