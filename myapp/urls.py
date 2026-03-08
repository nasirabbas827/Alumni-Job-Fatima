from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('verify-email/<int:user_id>/', views.verify_email, name='verify_email'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('reset-password/<int:user_id>/', views.reset_password, name='reset_password'),

    # Role-based dashboards
    path('dashboard/alumni/', views.alumni_dashboard, name='alumni_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/employer/', views.employer_dashboard, name='employer_dashboard'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('jobs/create/', views.create_job, name='create_job'),
    path('jobs/my-jobs/', views.my_jobs, name='my_jobs'),
    path('jobs/update/<int:job_id>/', views.update_job, name='update_job'),
    path('jobs/delete/<int:job_id>/', views.delete_job, name='delete_job'),
    path('jobs/', views.job_list, name='job_list'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('job/<int:job_id>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('my-job-applications/', views.my_job_applications, name='my_job_applications'),
    path('update-application-status/<int:application_id>/<str:status>/', views.update_application_status, name='update_application_status'),
    path('my-bookmarks/', views.my_bookmarks, name='my_bookmarks'),
    path('user-profile/<int:user_id>/', views.view_user_profile, name='view_user_profile'),

]

# For serving media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
