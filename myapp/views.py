from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.db.models import Q

from .forms import (
    UserRegisterForm, LoginForm, ProfileUpdateForm,
    PasswordResetRequestForm, SetNewPasswordForm,
    JobForm, JobApplicationForm
)
from .models import UserRegister, Job, JobApplication, Bookmark


# ────────────────────────────────────────────────
#   EMAIL NOTIFICATION HELPERS
# ────────────────────────────────────────────────

def send_new_job_notification(job):
    """Notify ALL users about a newly posted job"""
    subject = f"New Job Posted: {job.title}"
    message = f"""
A new job has been posted!

Title: {job.title}
Company/Employer: {job.employer.full_name}
Location: {job.location}
Category: {job.category}
Required Skills: {job.skills_required}


Best regards,
Job Portal Team
"""
    emails = UserRegister.objects.filter(
        status='approved', is_active=True
    ).values_list('email', flat=True)

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=list(emails),
        fail_silently=True,           # don't crash page if email fails
    )


def send_new_application_notification(application):
    """Notify the JOB OWNER (employer/alumni) about new application"""
    job = application.job
    applicant = application.applicant

    subject = f"New Application for {job.title}"
    message = f"""
Hello {job.employer.full_name},

A new application has been received for your job posting:

Job: {job.title}
Applicant: {applicant.full_name} ({applicant.email})
Role: {applicant.role}
Applied on: {application.applied_at.strftime('%Y-%m-%d %H:%M')}



Best regards,
Job Portal Team
"""
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[job.employer.email],
        fail_silently=True,
    )


def send_application_status_update_notification(application):
    """Notify the APPLICANT about status change"""
    job = application.job
    applicant = application.applicant

    subject = f"Update: Your application for {job.title}"
    message = f"""
Hello {applicant.full_name},

Your application status for the following job has been updated:

Job: {job.title}
Employer: {job.employer.full_name}
New Status: {application.get_status_display()}
Updated on: {application.updated_at.strftime('%Y-%m-%d %H:%M') if hasattr(application, 'updated_at') else 'recently'}



Best regards,
Job Portal Team
"""
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[applicant.email],
        fail_silently=True,
    )


# ────────────────────────────────────────────────
#   AUTHENTICATION & ACCOUNT VIEWS
# ────────────────────────────────────────────────

def index(request):
    return render(request, 'index.html')



def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.status = 'pending'
            user.save()

            verify_link = request.build_absolute_uri(
                reverse('verify_email', args=[user.id])
            )

            send_mail(
                subject="Verify Your Account",
                message=f"""
Hello {user.full_name},

Thank you for registering.

Please verify your email by clicking the link below:

{verify_link}

After verification you will be able to login.

Regards,
Job Portal System
""",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False
            )

            messages.success(
                request,
                "Registration successful. Please check your email to verify your account."
            )
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'register.html', {'form': form})


def verify_email(request, user_id):
    try:
        user = UserRegister.objects.get(id=user_id)
        if user.status != 'approved':
            user.status = 'approved'
            user.save()
        messages.success(request, "Email verified successfully. You can now login.")
    except UserRegister.DoesNotExist:
        messages.error(request, "Invalid verification link.")

    return redirect('login')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = UserRegister.objects.get(username=username)

                if not user.is_active:
                    messages.error(request, 'Your account is inactive. Contact admin.')
                    return redirect('login')

                if user.password != password:
                    messages.error(request, 'Invalid password.')
                    return redirect('login')

                if user.status == 'pending':
                    messages.warning(request, 'Please verify your email before logging in.')
                    return redirect('login')

                if user.status == 'rejected':
                    messages.error(request, 'Your account has been rejected by the admin.')
                    return redirect('login')

                # Session
                request.session['username'] = user.username
                request.session['role'] = user.role

                messages.success(request, 'Login successful!')

                if user.role == 'alumni':
                    return redirect('alumni_dashboard')
                elif user.role == 'student':
                    return redirect('student_dashboard')
                elif user.role == 'employer':
                    return redirect('employer_dashboard')
                else:
                    return redirect('login')

            except UserRegister.DoesNotExist:
                messages.error(request, 'Username does not exist.')

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    request.session.flush()
    messages.success(request, 'Logged out successfully.')
    return redirect('login')


# ────────────────────────────────────────────────
#   DASHBOARDS
# ────────────────────────────────────────────────

def alumni_dashboard(request):
    username = request.session.get('username')
    role = request.session.get('role')
    if not username or role != 'alumni':
        return redirect('login')
    return render(request, 'alumni_dashboard.html', {'username': username})


def student_dashboard(request):
    username = request.session.get('username')
    role = request.session.get('role')
    if not username or role != 'student':
        return redirect('login')
    return render(request, 'student_dashboard.html', {'username': username})


def employer_dashboard(request):
    username = request.session.get('username')
    role = request.session.get('role')
    if not username or role != 'employer':
        return redirect('login')
    return render(request, 'employer_dashboard.html', {'username': username})


# ────────────────────────────────────────────────
#   PROFILE & PASSWORD
# ────────────────────────────────────────────────

def update_profile(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    user = get_object_or_404(UserRegister, username=username)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')

            if user.role == 'alumni':
                return redirect('alumni_dashboard')
            elif user.role == 'student':
                return redirect('student_dashboard')
            elif user.role == 'employer':
                return redirect('employer_dashboard')
    else:
        form = ProfileUpdateForm(instance=user)

    return render(request, 'update_profile.html', {'form': form})


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = UserRegister.objects.get(email=email)
                reset_link = request.build_absolute_uri(
                    reverse('reset_password', args=[user.id])
                )

                send_mail(
                    "Password Reset",
                    f"""
Hello {user.full_name}

Click the link below to reset your password:

{reset_link}
""",
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False
                )

                messages.success(request, "Password reset link has been sent to your email.")
                return redirect('login')
            except UserRegister.DoesNotExist:
                messages.error(request, "Email not found.")
    else:
        form = PasswordResetRequestForm()

    return render(request, 'password_reset_request.html', {'form': form})


def reset_password(request, user_id):
    user = get_object_or_404(UserRegister, id=user_id)

    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user.password = form.cleaned_data['new_password']
            user.save()
            messages.success(request, "Password updated successfully.")
            return redirect('login')
    else:
        form = SetNewPasswordForm()

    return render(request, 'reset_password.html', {'form': form})


# ────────────────────────────────────────────────
#   JOBS – CREATE / LIST / UPDATE / DELETE
# ────────────────────────────────────────────────

def create_job(request):
    username = request.session.get('username')
    role = request.session.get('role')

    if not username or role not in ['alumni', 'employer']:
        return redirect('login')

    user = get_object_or_404(UserRegister, username=username)

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = user
            job.status = 'approved'  # ← consider making this pending & add admin approval flow later
            job.save()

            # ← NEW: Notify everyone about new job
            send_new_job_notification(job)

            messages.success(request, "Job posted successfully.")
            return redirect('my_jobs')
    else:
        form = JobForm()

    return render(request, 'create_job.html', {'form': form})


def my_jobs(request):
    username = request.session.get('username')
    role = request.session.get('role')

    if not username or role not in ['alumni', 'employer']:
        return redirect('login')

    user = get_object_or_404(UserRegister, username=username)
    jobs = Job.objects.filter(employer=user).order_by('-created_at')

    return render(request, 'my_jobs.html', {'jobs': jobs})


def update_job(request, job_id):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    user = get_object_or_404(UserRegister, username=username)
    job = get_object_or_404(Job, id=job_id, employer=user)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully.")
            return redirect('my_jobs')
    else:
        form = JobForm(instance=job)

    return render(request, 'update_job.html', {'form': form})


def delete_job(request, job_id):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    user = get_object_or_404(UserRegister, username=username)
    job = get_object_or_404(Job, id=job_id, employer=user)

    job.delete()
    messages.success(request, "Job deleted successfully.")

    return redirect('my_jobs')


# ────────────────────────────────────────────────
#   JOB BROWSING & APPLICATION
# ────────────────────────────────────────────────

def job_list(request):
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    category = request.GET.get('category', '')

    jobs = Job.objects.filter(status='approved')

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(skills_required__icontains=query)
        )
    if location:
        jobs = jobs.filter(location__icontains=location)
    if category:
        jobs = jobs.filter(category__icontains=category)

    # Simple skill matching score
    username = request.session.get('username')
    if username:
        user = get_object_or_404(UserRegister, username=username)
        if user.skills:
            user_skills = {s.strip().lower() for s in user.skills.split(',')}
            for job in jobs:
                job_skills = {s.strip().lower() for s in job.skills_required.split(',')}
                job.skill_match = len(user_skills & job_skills)

    return render(request, 'job_list.html', {
        'jobs': jobs,
        'query': query,
        'location': location,
        'category': category
    })


def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    username = request.session.get('username')
    user = None
    can_apply = False
    has_applied = False
    is_bookmarked = False

    if username:
        user = get_object_or_404(UserRegister, username=username)
        if user.role == 'alumni' and job.employer == user:
            can_apply = False
        else:
            can_apply = True
            has_applied = JobApplication.objects.filter(job=job, applicant=user).exists()
            is_bookmarked = Bookmark.objects.filter(user=user, job=job).exists()

    return render(request, 'job_detail.html', {
        'job': job,
        'can_apply': can_apply,
        'has_applied': has_applied,
        'is_bookmarked': is_bookmarked
    })


def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    username = request.session.get('username')

    if not username:
        return redirect('login')

    user = get_object_or_404(UserRegister, username=username)

    if job.employer == user and user.role == 'alumni':
        messages.error(request, "You cannot apply to your own job.")
        return redirect('job_detail', job_id=job.id)

    if request.method == 'POST':
        resume = request.FILES.get('resume')
        if not resume:
            messages.error(request, "Please upload your resume to apply.")
            return redirect('job_detail', job_id=job.id)

        application, created = JobApplication.objects.get_or_create(
            job=job,
            applicant=user,
            defaults={'resume': resume}
        )

        if created:
            messages.success(request, "Application submitted successfully.")
            # ← NEW: Notify employer/alumni
            send_new_application_notification(application)
        else:
            messages.info(request, "You have already applied to this job.")

    return redirect('job_detail', job_id=job.id)


def my_applications(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    user = get_object_or_404(UserRegister, username=username)
    applications = JobApplication.objects.filter(applicant=user).order_by('-applied_at')

    return render(request, 'my_applications.html', {'applications': applications})


# ────────────────────────────────────────────────
#   EMPLOYER / ALUMNI – APPLICATION MANAGEMENT
# ────────────────────────────────────────────────

def my_job_applications(request):
    username = request.session.get('username')
    role = request.session.get('role')

    if not username or role not in ['employer', 'alumni']:
        return redirect('login')

    user = get_object_or_404(UserRegister, username=username)
    jobs = Job.objects.filter(employer=user)
    applications = JobApplication.objects.filter(job__in=jobs).order_by('-applied_at')

    return render(request, 'my_job_applications.html', {'applications': applications})


def update_application_status(request, application_id, status):
    username = request.session.get('username')
    role = request.session.get('role')

    if not username or role not in ['employer', 'alumni']:
        return redirect('login')

    application = get_object_or_404(JobApplication, id=application_id)

    if application.job.employer.username != username:
        messages.error(request, "You cannot update this application.")
        return redirect('my_job_applications')

    if status not in dict(JobApplication.STATUS_CHOICES):
        messages.error(request, "Invalid status.")
        return redirect('my_job_applications')

    old_status = application.status
    application.status = status
    application.save()

    messages.success(request, f"Application status updated to {status}.")

    # ← NEW: Notify applicant if status actually changed
    if old_status != status:
        send_application_status_update_notification(application)

    return redirect('my_job_applications')


# ────────────────────────────────────────────────
#   BOOKMARKS
# ────────────────────────────────────────────────

def toggle_bookmark(request, job_id):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    user = get_object_or_404(UserRegister, username=username)
    job = get_object_or_404(Job, id=job_id)

    bookmark, created = Bookmark.objects.get_or_create(user=user, job=job)
    if not created:
        bookmark.delete()
        messages.info(request, "Removed from bookmarks.")
    else:
        messages.success(request, "Job bookmarked.")

    return redirect('job_detail', job_id=job.id)


def my_bookmarks(request):
    username = request.session.get('username')
    role = request.session.get('role')

    if not username or role not in ['student', 'alumni']:
        return redirect('login')

    user = get_object_or_404(UserRegister, username=username)
    bookmarks = Bookmark.objects.filter(user=user).select_related('job').order_by('-created_at')

    return render(request, 'my_bookmarks.html', {'bookmarks': bookmarks})

# View a public profile
def view_user_profile(request, user_id):
    user = get_object_or_404(UserRegister, id=user_id, is_public=True)
    return render(request, 'view_user_profile.html', {'profile_user': user})