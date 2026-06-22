from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    LEVEL_CHOICES = [
        ('fresher', 'Fresher'),
        ('junior', 'Junior'),
        ('mid', 'Mid-Level'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
        ('executive', 'Executive'),
    ]

    token_balance = models.IntegerField(default=10)
    profile_ready = models.BooleanField(default=False)

    # Core Profile Fields
    skills = models.TextField(blank=True, help_text="List your skills")
    experience = models.TextField(blank=True, help_text="Previous work experience")
    roles = models.TextField(blank=True, help_text="Roles you have held")
    cv = models.FileField(upload_to='cvs/', blank=True, null=True)
    interests = models.TextField(blank=True)
    fun_fact = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    availability_times = models.TextField(blank=True, help_text="Usual availability times")
    linkedin_link = models.URLField(blank=True)
    offerings = models.TextField(blank=True, help_text="Optional: things you can provide or share with others")

    years_of_experience = models.PositiveIntegerField(null=True, blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    study_field = models.CharField(max_length=255, blank=True, help_text="e.g. Computer Science")
    university = models.CharField(max_length=255, blank=True, help_text="University name")


    def get_level_display_label(self):
        return dict(self.LEVEL_CHOICES).get(self.level, '')

class Meeting(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed')
    )
    mentee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mentee_meetings')
    mentor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mentor_meetings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    why_choose_mentor = models.TextField()
    session_objectives = models.TextField()
    calendly_link = models.URLField(max_length=500, blank=True, null=True, help_text="Mentee's Calendly event link")
    token_escrowed = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class Evaluation(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='evaluations')
    evaluator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='given_evaluations')
    evaluatee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_evaluations')
    
    skills_rating = models.IntegerField(default=0)
    experience_rating = models.IntegerField(default=0)
    roles_rating = models.IntegerField(default=0)
    cv_rating = models.IntegerField(default=0)
    interest_rating = models.IntegerField(default=0)
    fun_fact_rating = models.IntegerField(default=0)
    summary_rating = models.IntegerField(default=0)
    
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('meeting', 'evaluator')
