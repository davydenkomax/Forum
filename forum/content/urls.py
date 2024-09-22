from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    path(
        'create-subject/',
        views.SubjectCreateView.as_view(),
        name='create_subject'
    ),
    path(
        'create-message/<int:subject_id>/<slug:subject_slug>/',
        views.MessageCreateView.as_view(),
        name='create_message'
    ),
    path(
        '',
        views.SectionListView.as_view(),
        name='section_list'
    ),
    path(
        'search-result/',
        views.FindSubjectListView.as_view(),
        name='search_result'
    ),
    path(
        '<slug:section_slug>/',
        views.SubjectListView.as_view(),
        name='subject_list_by_section'
    ),
    path(
        '<slug:section_slug>/<int:subject_id>/<slug:subject_slug>/',
        views.MessageListView.as_view(),
        name='list_message_by_subject'
    ),
    path(
        'create-update-content/<int:message_id>/',
        views.ContentCreateUpdateView.as_view(),
        name='create_update_content'
    ),
    path(
        'delete-content/<int:content_id>/',
        views.ContentDeleteView.as_view(),
        name='delete_content'
    ),
]