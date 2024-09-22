from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(
        template_name='register/login.html',
    ), name="login"),
    path("logout/", auth_views.LogoutView.as_view(
        template_name='register/logged_out.html'
    ), name="logout"),
    path(
        "password_change/", auth_views.PasswordChangeView.as_view(
            template_name='register/password_change_form.html'
        ), name="password_change"
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name='register/password_change_done.html'
        ),
        name="password_change_done",
    ),
    path("password_reset/", auth_views.PasswordResetView.as_view(
        template_name='register/password_reset_form.html'
    ), name="password_reset"),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name='register/password_reset_done.html'
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name='register/password_reset_confirm.html'
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name='register/password_reset_complete.html'
        ),
        name="password_reset_complete",
    ),
    path('registration/', views.RegisterView.as_view(), name='registration'),
    path('edit-profile/', views.ProfileUserUpdateView.as_view(), name='edit_profile'),
    path(
        'history-messages/',
        views.HistoryMessagesListView.as_view(),
        name='history_messages'
    ),
    path(
        'my-subjects/',
        views.SubjectsByAuthorListView.as_view(),
        name='subjects_by_author'
    ),
    path(
        'statistics-subject/<int:subject_id>/<slug:subject_slug>/',
        views.StatisticsSubject.as_view(),
        name='statistic_by_subject',
    )
]