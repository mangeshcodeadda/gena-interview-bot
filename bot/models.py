from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class JobDescription(models.Model):
    title = models.CharField(max_length=100)  # e.g., "Frontend Developer", "Data Analyst"
    skills = models.CharField(max_length=255)  # Comma-separated skills
    question_count = models.IntegerField(default=5)
    passing_score = models.IntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class InterviewAssignment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    )
    
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_interviews')
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name='assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    score = models.FloatField(null=True, blank=True)  # Percentage score
    eligibility = models.CharField(max_length=100, null=True, blank=True)  # e.g., "Highly Eligible", "Not Eligible"
    feedback = models.TextField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.candidate.username} - {self.job_description.title}"
    
    def is_expired(self):
        """Check if the interview assignment has expired"""
        return timezone.now() > self.deadline
    
    def save(self, *args, **kwargs):
        # Auto-update status to expired if deadline has passed
        if self.deadline and timezone.now() > self.deadline and self.status == 'pending':
            self.status = 'expired'
        super().save(*args, **kwargs)

class InterviewSession(models.Model):
    assignment = models.ForeignKey(InterviewAssignment, on_delete=models.CASCADE, related_name='sessions')
    session_id = models.CharField(max_length=100, unique=True)  # Unique session identifier
    current_question = models.IntegerField(default=1)  # Current question number
    conversation_history = models.JSONField(default=list)  # Store the entire conversation as JSON
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Session {self.session_id} for {self.assignment}"
    
    def is_complete(self):
        return self.current_question > self.assignment.job_description.question_count
