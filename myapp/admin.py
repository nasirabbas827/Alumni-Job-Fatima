from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import UserRegister, Job, JobApplication, Bookmark

# =====================================================
# UserRegister Admin
# =====================================================
@admin.register(UserRegister)
class UserRegisterAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'email', 'role', 'status', 'date_joined', 'is_active')
    list_filter = ('role', 'status', 'gender', 'is_active', 'date_joined')
    search_fields = ('username', 'full_name', 'email', 'phone', 'city', 'country')
    actions = ['approve_users', 'reject_users', 'export_users_csv']

    def approve_users(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} users approved.")
    approve_users.short_description = "Approve selected users"

    def reject_users(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f"{updated} users rejected.")
    reject_users.short_description = "Reject selected users"

    def export_users_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Full Name', 'Username', 'Email', 'Role', 'Status', 'Date Joined'])

        for user in queryset:
            writer.writerow([user.id, user.full_name, user.username, user.email, user.role, user.status, user.date_joined])
        return response
    export_users_csv.short_description = "Export selected users to CSV"

# =====================================================
# Job Admin
# =====================================================
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'location', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'employer__username', 'location', 'category')
    actions = ['approve_jobs', 'reject_jobs', 'export_jobs_csv']

    def approve_jobs(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} jobs approved.")
    approve_jobs.short_description = "Approve selected jobs"

    def reject_jobs(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f"{updated} jobs rejected.")
    reject_jobs.short_description = "Reject selected jobs"

    def export_jobs_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="jobs.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Title', 'Employer', 'Location', 'Category', 'Status', 'Created At'])

        for job in queryset:
            writer.writerow([job.id, job.title, job.employer.username, job.location, job.category, job.status, job.created_at])
        return response
    export_jobs_csv.short_description = "Export selected jobs to CSV"

# =====================================================
# JobApplication Admin
# =====================================================
@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('job__title', 'applicant__username')
    actions = ['export_applications_csv']

    def export_applications_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="applications.csv"'

        writer = csv.writer(response)
        writer.writerow(['Job', 'Applicant', 'Status', 'Applied At'])

        for app in queryset:
            writer.writerow([app.job.title, app.applicant.username, app.status, app.applied_at])
        return response
    export_applications_csv.short_description = "Export selected applications to CSV"

# =====================================================
# Bookmark Admin
# =====================================================
@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'job__title')
    actions = ['export_bookmarks_csv']

    def export_bookmarks_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bookmarks.csv"'

        writer = csv.writer(response)
        writer.writerow(['User', 'Job', 'Created At'])

        for bm in queryset:
            writer.writerow([bm.user.username, bm.job.title, bm.created_at])
        return response
    export_bookmarks_csv.short_description = "Export selected bookmarks to CSV"