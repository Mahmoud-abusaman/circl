from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-mentorships/', views.my_mentorships, name='my_mentorships'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('meeting/request/<int:mentor_id>/', views.request_meeting, name='request_meeting'),
    path('meeting/action/<int:meeting_id>/<str:action>/', views.meeting_action, name='meeting_action'),
    path('meeting/evaluate/<int:meeting_id>/', views.evaluate_meeting, name='evaluate_meeting'),
    path('', views.dashboard, name='home'),
]
