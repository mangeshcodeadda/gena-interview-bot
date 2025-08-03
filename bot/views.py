from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
import json
import uuid
import openai
import os
import pyttsx3
from .models import JobDescription, InterviewAssignment, InterviewSession
from dotenv import load_dotenv
load_dotenv()

def homepage(request):
    """Render the homepage with information about the interview bot"""
    return render(request, 'homepage.html')

# OpenAI and Google Cloud TTS Helper Functions
def initialize_openai_client():
    """Initialize and return OpenAI client"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables")
    
    client = openai.OpenAI(api_key=api_key)
    return client

def generate_interview_question(session):
    """Generate an interview question and audio using OpenAI and Google Cloud TTS"""
    try:
        # Get job description details
        assignment = session.assignment
        job_description = assignment.job_description
        skills = job_description.skills.split(',')
        current_question = session.current_question
        total_questions = job_description.question_count
        
        # Get conversation history
        conversation_history = session.conversation_history
        
        # Initialize OpenAI client
        client = initialize_openai_client()
        
        # Prepare system prompt
        system_prompt = f"""You are an AI interviewer for a {job_description.title} position. 
        You are conducting a technical interview to assess the candidate's skills in {', '.join(skills)}.
        This is question {current_question} of {total_questions}.
        Ask a specific, challenging but fair technical question related to one of these skills.
        The question should be different from previous questions in this interview.
        Format your response as a clear, direct question without any preamble or additional text.

        Note: Do not include any answer in your response if user has not given any answer or pretends to not answer 
        You just have to ask the question.
        """
        
        # Prepare conversation history for OpenAI
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add previous conversation if any
        for item in conversation_history:
            role = "assistant" if item.get('role') == "assistant" else "user"
            messages.append({"role": role, "content": item.get('content', '')})
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )
        
        question = response.choices[0].message.content.strip()
        
        # Generate audio for the question (Google Cloud TTS)
        audio_url = generate_question_audio(question)
        
        return {"question": question, "audio_url": audio_url}
    
    except Exception as e:
        # Fallback question in case of API failure
        fallback_question = f"Technical question for {job_description.title} position (Error: {str(e)}): Please describe your experience with {skills[0] if skills else 'relevant technologies'}."
        return {"question": fallback_question, "audio_url": None}

def generate_question_audio(question_text):
    """Generate audio for a question using open-source pyttsx3 TTS"""
    import logging
    logger = logging.getLogger(__name__)
    try:
        import pyttsx3
        audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', 'audio')
        os.makedirs(audio_dir, exist_ok=True)
        filename = f"question_{uuid.uuid4()}.mp3"
        filepath = os.path.join(audio_dir, filename)

        # Initialize pyttsx3 engine
        engine = pyttsx3.init()
        # Optionally set properties (rate, volume, voice)
        engine.setProperty('rate', 170)
        engine.setProperty('volume', 1.0)
        # Save to file (pyttsx3 natively supports wav, but with ffmpeg installed, mp3 works via pydub)
        try:
            engine.save_to_file(question_text, filepath)
            engine.runAndWait()
        except Exception as e:
            logger.error(f"pyttsx3 failed to generate audio: {str(e)}")
            return None
        logger.info(f"Audio file written: {filepath}")
        url = f"/media/audio/{filename}"
        logger.info(f"Returning audio URL: {url}")
        return url
    except Exception as e:
        logger.error(f"Error generating audio (pyttsx3): {str(e)}")
        return None

def evaluate_interview(session):
    """Evaluate the interview and generate score, eligibility, and feedback"""
    try:
        # Get job description and conversation history
        assignment = session.assignment
        job_description = assignment.job_description
        conversation_history = session.conversation_history
        
        # Initialize OpenAI client
        client = initialize_openai_client()
        
        # Prepare system prompt for evaluation
        system_prompt = f"""You are an AI interview evaluator for a {job_description.title} position.
        Evaluate the candidate's responses to the technical questions based on accuracy, depth of knowledge, and clarity.
        Provide a score from 0-100, an eligibility percentage, and detailed feedback.
        Format your response as JSON with the following structure:
        {{
            "score": <0-100>,
            "eligibility": <0-100>,
            "feedback": "<overall feedback>",
            "question_feedback": [{{"question_number": 1, "feedback": "<feedback for question 1>"}}, ...]
        }}
        """
        
        # Prepare conversation for OpenAI
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Job Skills: {job_description.skills}\n\nInterview Conversation:\n{json.dumps(conversation_history, indent=2)}"}
        ]
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        # Parse the evaluation
        evaluation = json.loads(response.choices[0].message.content)
        print("Evaluation:", evaluation)
        score = evaluation.get('score', 70)  # Default score if not provided
        eligibility = evaluation.get('eligibility', 50)  # Default eligibility if not provided
        feedback = evaluation.get('feedback', 'No feedback available.')
        
        # Store question feedback in session for detailed results
        session.question_feedback = evaluation.get('question_feedback', [])
        session.save()
        
        return score, eligibility, feedback
    
    except Exception as e:
        # Return default values in case of API failure
        print(f"Error evaluating interview: {str(e)}")
        return 70, 50, f"Interview evaluation could not be completed due to an error: {str(e)}"


# Authentication Views
def login_view(request):
    if request.user.is_authenticated:
        # Redirect based on user role
        if request.user.groups.filter(name='Admin').exists():
            return redirect('admin_dashboard')
        else:
            return redirect('candidate_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Redirect based on user role
            if user.groups.filter(name='Admin').exists():
                return redirect('admin_dashboard')
            else:
                return redirect('candidate_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'auth/login.html')

def signup_view(request):
    if request.user.is_authenticated:
        # Redirect based on user role
        if request.user.groups.filter(name='Admin').exists():
            return redirect('admin_dashboard')
        else:
            return redirect('candidate_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')
        
        # Validate form data
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'auth/signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'auth/signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'auth/signup.html')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)
        
        # Assign role
        if role == 'admin':
            admin_group, created = Group.objects.get_or_create(name='Admin')
            user.groups.add(admin_group)
        else:
            candidate_group, created = Group.objects.get_or_create(name='Candidate')
            user.groups.add(candidate_group)
        
        # Log in the user
        login(request, user)
        
        # Redirect based on role
        if role == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('candidate_dashboard')
    
    return render(request, 'auth/signup.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard Views
@login_required
def admin_dashboard(request):
    # Check if user is an admin
    if not request.user.groups.filter(name='Admin').exists():
        messages.error(request, 'You do not have permission to access the admin dashboard')
        return redirect('candidate_dashboard')
    
    # Get all job descriptions
    job_descriptions = JobDescription.objects.all().order_by('-created_at')
    
    # Get all interview assignments
    interview_assignments = InterviewAssignment.objects.all().order_by('-assigned_at')
    
    context = {
        'job_descriptions': job_descriptions,
        'interview_assignments': interview_assignments,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def candidate_dashboard(request):
    # Check if user is a candidate
    if not request.user.groups.filter(name='Candidate').exists():
        messages.error(request, 'You do not have permission to access the candidate dashboard')
        return redirect('admin_dashboard')
    
    # Get all interview assignments for the candidate
    assignments = InterviewAssignment.objects.filter(candidate=request.user).order_by('-assigned_at')
    
    # Update expired assignments
    for assignment in assignments:
        if assignment.status == 'pending' and assignment.is_expired():
            assignment.status = 'expired'
            assignment.save()
    
    # Categorize assignments by status
    pending_assignments = assignments.filter(status='pending')
    in_progress_assignments = assignments.filter(status='in_progress')
    completed_assignments = assignments.filter(status='completed')
    expired_assignments = assignments.filter(status='expired')
    
    context = {
        'pending_assignments': pending_assignments,
        'in_progress_assignments': in_progress_assignments,
        'completed_assignments': completed_assignments,
        'expired_assignments': expired_assignments,
    }
    
    return render(request, 'dashboard/candidate_dashboard.html', context)

# Interview Session Views
@login_required
def start_interview(request, assignment_id):
    """Start or resume an interview session"""
    # Check if user is a candidate
    if not request.user.groups.filter(name='Candidate').exists():
        messages.error(request, 'You do not have permission to access this interview')
        return redirect('admin_dashboard')
    
    # Get the interview assignment
    assignment = get_object_or_404(InterviewAssignment, id=assignment_id, candidate=request.user)
    
    # Check if the assignment is expired
    if assignment.status == 'expired' or assignment.is_expired():
        messages.error(request, 'This interview has expired')
        return redirect('candidate_dashboard')
    
    # Check if the assignment is already completed
    if assignment.status == 'completed':
        return redirect('interview_results', assignment_id=assignment_id)
    
    # Get or create an interview session
    try:
        session = InterviewSession.objects.get(assignment=assignment)
    except InterviewSession.DoesNotExist:
        # Create a new session with a unique ID
        session_id = str(uuid.uuid4())
        session = InterviewSession.objects.create(
            assignment=assignment,
            session_id=session_id,
            current_question=1,
            conversation_history=[]
        )
        # Update assignment status to in_progress
        assignment.status = 'in_progress'
        assignment.save()
    
    # Calculate progress percentage
    progress_percentage = (session.current_question - 1) / assignment.job_description.question_count * 100
    
    # Calculate time remaining until deadline
    now = timezone.now()
    time_remaining = assignment.deadline - now
    days = time_remaining.days
    hours, remainder = divmod(time_remaining.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_remaining_str = f"{days}d {hours}h {minutes}m"
    
    # If this is a new session or we need a new question, generate one
    conversation_history = session.conversation_history
    if not conversation_history or conversation_history[-1]['role'] != 'assistant':
        # Generate the first/next question
        question_obj = generate_interview_question(session)
        
        # Add the question and audio to conversation history
        conversation_history.append({
            'role': 'assistant',
            'content': question_obj['question'],
            'question_number': session.current_question,
            'audio_url': question_obj['audio_url']
        })
        
        # Save updated conversation history
        session.conversation_history = conversation_history
        session.save()
    
    # Get the last question's audio_url for the template (if any)
    audio_url = None
    for msg in reversed(conversation_history):
        if msg.get('role') == 'assistant' and msg.get('audio_url'):
            audio_url = msg['audio_url']
            break

    context = {
        'assignment': assignment,
        'session': session,
        'conversation_history': conversation_history,
        'progress_percentage': progress_percentage,
        'time_remaining': time_remaining_str,
        'audio_url': audio_url
    }
    
    return render(request, 'interview/interview_session.html', context)

@login_required
@require_POST
def submit_response(request, session_id):
    """Handle candidate's response submission"""
    # Check if user is a candidate
    if not request.user.groups.filter(name='Candidate').exists():
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    # Get the session
    session = get_object_or_404(InterviewSession, session_id=session_id)
    assignment = session.assignment
    
    # Verify the candidate owns this session
    if assignment.candidate != request.user:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    # Check if the assignment is expired
    if assignment.is_expired():
        return JsonResponse({'status': 'error', 'message': 'Interview has expired'}, status=400)
    
    # Parse the response from JSON
    try:
        data = json.loads(request.body)
        response = data.get('response')
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid request format'}, status=400)
    
    if not response:
        return JsonResponse({'status': 'error', 'message': 'Response is required'}, status=400)
    
    # Add the response to conversation history
    conversation_history = session.conversation_history
    conversation_history.append({
        'role': 'user',
        'content': response
    })
    
    # Check if this was the last question
    job_description = assignment.job_description
    is_last_question = session.current_question >= job_description.question_count
    
    if is_last_question:
        # Complete the interview
        assignment.status = 'completed'
        assignment.completed_at = timezone.now()
        
        # Generate score and feedback
        score, eligibility, feedback = evaluate_interview(session)
        
        assignment.score = score
        assignment.eligibility = eligibility
        assignment.feedback = feedback
        assignment.save()
        
        # Save the final conversation history
        session.conversation_history = conversation_history
        session.save()
        
        return JsonResponse({
            'status': 'success',
            'interview_complete': True,
            'redirect_url': f'/interview-results/{assignment.id}/'
        })
    else:
        # Move to the next question
        session.current_question += 1
        
        # Generate the next question
        next_question_obj = generate_interview_question(session)
        
        # Add the question and audio to conversation history
        conversation_history.append({
            'role': 'assistant',
            'content': next_question_obj['question'],
            'question_number': session.current_question,
            'audio_url': next_question_obj['audio_url']
        })
        
        # Save updated session
        session.conversation_history = conversation_history
        session.save()
        
        # Calculate new progress percentage
        progress_percentage = (session.current_question - 1) / job_description.question_count * 100
        
        return JsonResponse({
            'status': 'success',
            'interview_complete': False,
            'next_question': next_question_obj['question'],
            'audio_url': next_question_obj['audio_url'],
            'current_question': session.current_question,
            'progress_percentage': progress_percentage
        })

@login_required
def interview_results(request, assignment_id):
    """Display interview results and feedback"""
    # Get the interview assignment
    assignment = get_object_or_404(InterviewAssignment, id=assignment_id)
    
    # Check if the user is authorized to view these results
    if assignment.candidate != request.user and not request.user.groups.filter(name='Admin').exists():
        messages.error(request, 'You do not have permission to view these results')
        return redirect('candidate_dashboard' if request.user.groups.filter(name='Candidate').exists() else 'admin_dashboard')
    
    # Check if the interview is completed
    if assignment.status != 'completed':
        messages.error(request, 'This interview is not yet completed')
        return redirect('candidate_dashboard' if request.user.groups.filter(name='Candidate').exists() else 'admin_dashboard')
    
    # Get the session and extract question-answer pairs
    session = get_object_or_404(InterviewSession, assignment=assignment)
    conversation_history = session.conversation_history
    
    # Format the conversation history into question-answer pairs with feedback
    question_answers = []
    for i in range(0, len(conversation_history), 2):
        if i + 1 < len(conversation_history):
            qa_pair = {
                'question': conversation_history[i]['content'],
                'answer': conversation_history[i + 1]['content'],
                'feedback': f"Feedback for question {i//2 + 1} will be displayed here."  # Placeholder
            }
            question_answers.append(qa_pair)
    
    context = {
        'assignment': assignment,
        'question_answers': question_answers
    }
    
    return render(request, 'interview/interview_results.html', context)

# Job Description Management Views
@login_required
def job_description_create(request):
    # Check if user is admin
    if not request.user.groups.filter(name='Admin').exists():
        messages.error(request, 'You do not have permission to create job descriptions')
        return redirect('candidate_dashboard')
    
    if request.method == 'POST':
        # Process form data
        title = request.POST.get('title')
        skills = request.POST.get('skills')
        question_count = request.POST.get('question_count')
        
        # Validate data
        if not title or not skills or not question_count:
            messages.error(request, 'All fields are required')
            return render(request, 'dashboard/job_description_form.html')
        
        # Create job description
        job_description = JobDescription.objects.create(
            title=title,
            skills=skills,
            question_count=int(question_count)
        )
        
        messages.success(request, f'Job Description "{title}" created successfully')
        return redirect('admin_dashboard')
    
    return render(request, 'dashboard/job_description_form.html')

@login_required
def job_description_edit(request, jd_id):
    # Check if user is admin
    if not request.user.groups.filter(name='Admin').exists():
        messages.error(request, 'You do not have permission to edit job descriptions')
        return redirect('candidate_dashboard')
    
    # Get job description
    try:
        job_description = JobDescription.objects.get(id=jd_id)
    except JobDescription.DoesNotExist:
        messages.error(request, 'Job Description not found')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        # Process form data
        title = request.POST.get('title')
        skills = request.POST.get('skills')
        question_count = request.POST.get('question_count')
        
        # Validate data
        if not title or not skills or not question_count:
            messages.error(request, 'All fields are required')
            return render(request, 'dashboard/job_description_form.html', {'form': {'instance': job_description}})
        
        # Update job description
        job_description.title = title
        job_description.skills = skills
        job_description.question_count = int(question_count)
        job_description.save()
        
        messages.success(request, f'Job Description "{title}" updated successfully')
        return redirect('admin_dashboard')
    
    return render(request, 'dashboard/job_description_form.html', {'form': {'instance': job_description}})

@login_required
def job_description_delete(request, jd_id):
    # Check if user is admin
    if not request.user.groups.filter(name='Admin').exists():
        messages.error(request, 'You do not have permission to delete job descriptions')
        return redirect('candidate_dashboard')
    
    # Get job description
    try:
        job_description = JobDescription.objects.get(id=jd_id)
    except JobDescription.DoesNotExist:
        messages.error(request, 'Job Description not found')
        return redirect('admin_dashboard')
    
    # Delete job description
    job_description.delete()
    
    messages.success(request, 'Job Description deleted successfully')
    return redirect('admin_dashboard')

# Interview Assignment Views
@login_required
def assign_interview(request):
    # Check if user is admin
    if not request.user.groups.filter(name='Admin').exists():
        messages.error(request, 'You do not have permission to assign interviews')
        return redirect('candidate_dashboard')
    
    # Get all job descriptions and candidates
    job_descriptions = JobDescription.objects.all()
    candidates = User.objects.filter(groups__name='Candidate')
    
    if request.method == 'POST':
        # Process form data
        candidate_id = request.POST.get('candidate')
        job_description_id = request.POST.get('job_description')
        deadline_str = request.POST.get('deadline')
        
        # Validate data
        if not candidate_id or not job_description_id or not deadline_str:
            messages.error(request, 'All fields are required')
            return render(request, 'dashboard/assign_interview.html', {
                'job_descriptions': job_descriptions,
                'candidates': candidates
            })
        
        try:
            candidate = User.objects.get(id=candidate_id)
            job_description = JobDescription.objects.get(id=job_description_id)
            deadline = timezone.datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
            deadline = timezone.make_aware(deadline) if timezone.is_naive(deadline) else deadline
            
            # Create interview assignment
            assignment = InterviewAssignment.objects.create(
                candidate=candidate,
                job_description=job_description,
                deadline=deadline
            )
            assignment.save()
            messages.success(request, f'Interview assigned to {candidate.username} successfully')
            return redirect('admin_dashboard')
        except (User.DoesNotExist, JobDescription.DoesNotExist, ValueError) as e:
            messages.error(request, f'Error assigning interview: {str(e)}')
    
    context = {
        'job_descriptions': job_descriptions,
        'candidates': candidates
    }
    
    return render(request, 'dashboard/assign_interview.html', context)
