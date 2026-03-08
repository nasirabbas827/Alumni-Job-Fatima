from django.db import models

class UserRegister(models.Model):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField()

    # User role
    ROLE_CHOICES = [
        ('alumni', 'Alumni'),
        ('student', 'Student'),
        ('employer', 'Employer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Account approval status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Basic contact info
    phone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    # Profile information
    education = models.CharField(max_length=255, blank=True)
    skills = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    contact_number = models.CharField(max_length=15, blank=True)

    # Resume upload
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)

    # Profile visibility
    is_public = models.BooleanField(default=True)

    # Account metadata
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.status})"
    

# =====================================================
# 4. Job Posting Model
# =====================================================

class Job(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    employer = models.ForeignKey(
        UserRegister,
        on_delete=models.CASCADE,
        limit_choices_to={'role__in': ['employer', 'alumni']},
        related_name='jobs'
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)

    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    category = models.CharField(max_length=255)
    skills_required = models.TextField(help_text="Comma separated skills")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.employer.username}"




# JobApplication model
class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(
        UserRegister,  # <- use UserRegister instead of settings.AUTH_USER_MODEL
        on_delete=models.CASCADE,
        limit_choices_to={'role__in': ['student', 'alumni']}
    )
    resume = models.FileField(upload_to='applications/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'applicant')

    def __str__(self):
        return f"{self.applicant.username} -> {self.job.title}"
    
class Bookmark(models.Model):
    user = models.ForeignKey(UserRegister, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.username} bookmarked {self.job.title}"
