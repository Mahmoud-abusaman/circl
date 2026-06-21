from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Avg
from .models import CustomUser, Meeting, Evaluation
from django.utils import timezone
import datetime

def register_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not all([full_name, email, password, confirm_password]):
            messages.error(request, 'All fields are required.')
            return render(request, 'register.html')
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')
        if CustomUser.objects.filter(username=email).exists() or CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'register.html')
        
        user = CustomUser.objects.create_user(username=email, email=email, password=password)
        user.first_name = full_name
        user.save()
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile_edit')
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if not user.profile_ready:
                return redirect('profile_edit')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid input credentials.')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_edit(request):
    if request.method == 'POST':
        skills = request.POST.get('skills', '')
        experience = request.POST.get('experience', '')
        roles = request.POST.get('roles', '')
        interests = request.POST.get('interests', '')
        fun_fact = request.POST.get('fun_fact', '')
        summary = request.POST.get('summary', '')
        availability_times = request.POST.get('availability_times', '')
        linkedin_link = request.POST.get('linkedin_link', '').strip()
        offerings = request.POST.get('offerings', '')
        cv = request.FILES.get('cv')
        years_of_experience = request.POST.get('years_of_experience', '').strip()
        level = request.POST.get('level', '').strip()
        birth_date = request.POST.get('birth_date', '').strip()
        study_field = request.POST.get('study_field', '').strip()
        university = request.POST.get('university', '').strip()

        # Validate required fields
        errors = []
        if not all([skills, experience, roles, summary]):
            errors.append('Skills, Experience, Roles, and Summary are required.')
        if not linkedin_link:
            errors.append('LinkedIn profile link is required.')
        if not years_of_experience or not years_of_experience.isdigit():
            errors.append('Valid years of experience is required.')
        if not level:
            errors.append('Career level is required.')
        if not birth_date:
            errors.append('Birth date is required.')
        if not study_field:
            errors.append('Study field is required.')
        if not university:
            errors.append('University name is required.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'profile_edit.html')
        
        user = request.user
        user.skills = skills
        user.experience = experience
        user.roles = roles
        user.interests = interests
        user.fun_fact = fun_fact
        user.summary = summary
        user.availability_times = availability_times
        user.linkedin_link = linkedin_link
        user.offerings = offerings
        user.years_of_experience = int(years_of_experience)
        user.level = level
        user.study_field = study_field
        user.university = university
        if cv:
            user.cv = cv
        try:
            user.birth_date = datetime.date.fromisoformat(birth_date)
        except ValueError:
            messages.error(request, 'Invalid birth date format.')
            return render(request, 'profile_edit.html')

        user.profile_ready = True
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('dashboard')
        
    return render(request, 'profile_edit.html')

@login_required
def user_profile(request, user_id):
    profile_user = get_object_or_404(CustomUser, id=user_id, profile_ready=True)
    # Compute average rating received
    avg_ratings = Evaluation.objects.filter(evaluatee=profile_user).aggregate(
        avg_skills=Avg('skills_rating'),
        avg_experience=Avg('experience_rating'),
        avg_roles=Avg('roles_rating'),
        avg_summary=Avg('summary_rating'),
    )
    total_evals = Evaluation.objects.filter(evaluatee=profile_user).count()
    
    context = {
        'profile_user': profile_user,
        'avg_ratings': avg_ratings,
        'total_evals': total_evals,
        'can_request': profile_user != request.user,
    }
    return render(request, 'user_profile.html', context)

@login_required
def evaluate_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    if meeting.status != 'COMPLETED':
        messages.error(request, "Only completed meetings can be evaluated.")
        return redirect('dashboard')
    
    if request.user != meeting.mentee and request.user != meeting.mentor:
        messages.error(request, "Unauthorized.")
        return redirect('dashboard')

    # Who is being evaluated?
    evaluatee = meeting.mentor if request.user == meeting.mentee else meeting.mentee

    if Evaluation.objects.filter(meeting=meeting, evaluator=request.user).exists():
        messages.error(request, "You have already evaluated this meeting.")
        return redirect('dashboard')

    if request.method == 'POST':
        skills_rating = request.POST.get('skills_rating', 0)
        experience_rating = request.POST.get('experience_rating', 0)
        roles_rating = request.POST.get('roles_rating', 0)
        cv_rating = request.POST.get('cv_rating', 0)
        interest_rating = request.POST.get('interest_rating', 0)
        fun_fact_rating = request.POST.get('fun_fact_rating', 0)
        summary_rating = request.POST.get('summary_rating', 0)
        comments = request.POST.get('comments', '')

        Evaluation.objects.create(
            meeting=meeting,
            evaluator=request.user,
            evaluatee=evaluatee,
            skills_rating=skills_rating,
            experience_rating=experience_rating,
            roles_rating=roles_rating,
            cv_rating=cv_rating,
            interest_rating=interest_rating,
            fun_fact_rating=fun_fact_rating,
            summary_rating=summary_rating,
            comments=comments
        )
        messages.success(request, "Evaluation submitted successfully.")
        
        if request.user == meeting.mentee:
            return redirect('my_mentorships')
        else:
            return redirect('my_requests')

    return render(request, 'evaluate.html', {'meeting': meeting, 'evaluatee': evaluatee})

@login_required
def dashboard(request):
    user = request.user
    if not user.profile_ready:
        return redirect('profile_edit')
    
    query = request.GET.get('q', '').strip()
    
    if query:
        # Search mentors by name, roles, skills
        all_users = CustomUser.objects.filter(
            Q(first_name__icontains=query) |
            Q(skills__icontains=query) |
            Q(roles__icontains=query) |
            Q(study_field__icontains=query)
        ).exclude(id=user.id).filter(profile_ready=True).distinct()
        recommended_mentors = all_users[:20] # Show more for search
    else:
        # Recommended list based on recent users
        all_users = CustomUser.objects.exclude(id=user.id).filter(profile_ready=True).order_by('-date_joined')
        recommended_mentors = all_users[:6]
    
    # Just show a tiny snippet of recent meetings
    recent_mentee = Meeting.objects.filter(mentee=user).order_by('-created_at')[:3]
    recent_mentor = Meeting.objects.filter(mentor=user).order_by('-created_at')[:3]
    
    context = {
        'recent_mentee': recent_mentee,
        'recent_mentor': recent_mentor,
        'recommended_mentors': recommended_mentors,
        'query': query,
    }
    return render(request, 'dashboard.html', context)

@login_required
def my_mentorships(request):
    user = request.user
    if not user.profile_ready:
        return redirect('profile_edit')
        
    mentee_meetings = Meeting.objects.filter(mentee=user).order_by('-created_at')
    evaluated_meeting_ids = Evaluation.objects.filter(evaluator=user).values_list('meeting_id', flat=True)
    
    context = {
        'meetings': mentee_meetings,
        'evaluated_meeting_ids': evaluated_meeting_ids
    }
    return render(request, 'my_mentorships.html', context)

@login_required
def my_requests(request):
    user = request.user
    if not user.profile_ready:
        return redirect('profile_edit')
        
    mentor_meetings = Meeting.objects.filter(mentor=user).order_by('-created_at')
    evaluated_meeting_ids = Evaluation.objects.filter(evaluator=user).values_list('meeting_id', flat=True)
    
    context = {
        'meetings': mentor_meetings,
        'evaluated_meeting_ids': evaluated_meeting_ids
    }
    return render(request, 'my_requests.html', context)

@login_required
def request_meeting(request, mentor_id):
    if not request.user.profile_ready:
        return redirect('profile_edit')
        
    mentor = get_object_or_404(CustomUser, id=mentor_id)
    if mentor == request.user:
        messages.error(request, "You cannot request a meeting with yourself.")
        return redirect('dashboard')

    if request.method == 'POST':
        why_choose = request.POST.get('why_choose_mentor', '')
        objectives = request.POST.get('session_objectives', '')
        calendly_link = request.POST.get('calendly_link', '').strip()
        
        if not all([why_choose, objectives, calendly_link]):
            messages.error(request, 'All fields are required.')
            return render(request, 'request_meeting.html', {'mentor': mentor})

        try:
            with transaction.atomic():
                mentee = CustomUser.objects.select_for_update().get(id=request.user.id)
                if mentee.token_balance < 1:
                    messages.error(request, "Insufficient tokens to request. Need at least 1.")
                    return redirect('dashboard')
                    
                mentee.token_balance -= 1
                mentee.save()
                
                meeting = Meeting.objects.create(
                    mentee=mentee,
                    mentor=mentor,
                    why_choose_mentor=why_choose,
                    session_objectives=objectives,
                    calendly_link=calendly_link,
                    status='PENDING',
                    token_escrowed=1
                )
                
            messages.success(request, 'Meeting requested successfully!')
            return redirect('my_mentorships')
            
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            
            referer = request.META.get('HTTP_REFERER')
            if referer:
                return redirect(referer)
            return redirect('dashboard')

    return render(request, 'request_meeting.html', {'mentor': mentor})

@login_required
def meeting_action(request, meeting_id, action):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    user = request.user

    try:
        with transaction.atomic():
            meeting = Meeting.objects.select_for_update().get(id=meeting_id)
            mentee = CustomUser.objects.select_for_update().get(id=meeting.mentee.id)
            mentor = CustomUser.objects.select_for_update().get(id=meeting.mentor.id)

            if action == 'accept':
                if user != mentor:
                    raise Exception("Only mentor can accept.")
                if meeting.status != 'PENDING':
                    raise Exception("Meeting is not pending.")
                
                if mentee.token_balance < 4:
                    raise Exception("Mentee has insufficient tokens to proceed.")
                    
                mentee.token_balance -= 4
                mentee.save()
                
                meeting.token_escrowed += 4
                meeting.status = 'ACCEPTED'
                meeting.save()
                messages.success(request, "Meeting accepted.")

            elif action == 'reject':
                if user not in [mentee, mentor]:
                    raise Exception("Unauthorized.")
                if meeting.status != 'PENDING':
                    raise Exception("Meeting is not pending.")
                
                meeting.status = 'REJECTED'
                mentee.token_balance += meeting.token_escrowed
                mentee.save()
                
                meeting.token_escrowed = 0
                meeting.save()
                messages.success(request, "Meeting rejected and tokens refunded to mentee.")
                
            elif action == 'complete':
                if user != mentor:
                    raise Exception("Only the mentor can mark the meeting as complete.")
                if meeting.status != 'ACCEPTED':
                    raise Exception("Meeting must be accepted to complete.")
                
                meeting.status = 'COMPLETED'
                mentor.token_balance += meeting.token_escrowed
                mentor.save()
                
                meeting.token_escrowed = 0
                meeting.save()
                messages.success(request, "Meeting completed and tokens awarded to mentor.")
            else:
                messages.error(request, "Invalid action.")
    except Exception as e:
        messages.error(request, str(e))

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('dashboard')
