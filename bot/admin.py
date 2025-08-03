from django.contrib import admin
from .models import JobDescription, InterviewAssignment, InterviewSession

@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'skills', 'question_count', 'created_at')
    search_fields = ('title', 'skills')
    list_filter = ('created_at',)

@admin.register(InterviewAssignment)
class InterviewAssignmentAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job_description', 'deadline', 'status', 'score')
    list_filter = ('status', 'deadline')
    search_fields = ('candidate__username', 'job_description__title')
    raw_id_fields = ('candidate', 'job_description')

@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'assignment', 'current_question', 'started_at', 'last_activity')
    search_fields = ('session_id', 'assignment__candidate__username')
    list_filter = ('started_at',)
