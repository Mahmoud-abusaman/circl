import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solo_project.settings')
django.setup()

from core.models import CustomUser, Meeting, Evaluation
from django.contrib.auth.hashers import make_password

print("Cleaning existing data...")
CustomUser.objects.all().delete()
Meeting.objects.all().delete()
Evaluation.objects.all().delete()

print("Creating users...")

# Mentors
mentor1 = CustomUser.objects.create(
    username='alice@example.com',
    first_name='Alice',
    last_name='Smith',
    email='alice@example.com',
    password=make_password('password123'),
    profile_ready=True,
    years_of_experience=8,
    level='senior',
    birth_date=date(1990, 5, 12),
    study_field='Computer Science',
    university='MIT',
    linkedin_link='https://linkedin.com/in/alicesmith',
    skills='Python, Django, PostgreSQL, API Design, System Architecture',
    roles='Senior Backend Engineer, Tech Lead',
    experience='8 years building scalable backend systems for major tech companies.\nLead a team of 5 backend engineers.',
    summary='Passionate about scalable architectures and helping juniors level up to senior roles.',
    interests='Open Source, System Architecture, AI, Distributed Systems',
    fun_fact='I once wrote a compiler using only emojis.',
    availability_times='Monday to Thursday, 6PM - 9PM EST',
    offerings='Architecture reviews, backend mock interviews, career progression guidance.',
    token_balance=30
)

mentor2 = CustomUser.objects.create(
    username='bob@example.com',
    first_name='Bob',
    last_name='Johnson',
    email='bob@example.com',
    password=make_password('password123'),
    profile_ready=True,
    years_of_experience=12,
    level='lead',
    birth_date=date(1985, 8, 20),
    study_field='Software Engineering',
    university='Stanford',
    linkedin_link='https://linkedin.com/in/bobjohnson',
    skills='React, Node.js, TypeScript, Next.js, UI/UX',
    roles='Lead Frontend Engineer',
    experience='12 years crafting pixel-perfect interfaces.\nSpecialized in web accessibility and design systems.',
    summary='I love frontend engineering. I focus on accessibility, performance, and beautiful animations.',
    interests='UI design, UX, Accessibility, WebAssembly, CSS Art',
    fun_fact='I own 14 different custom mechanical keyboards.',
    availability_times='Weekends 10AM - 2PM PST',
    offerings='Portfolio reviews, frontend deep dives, React interview prep.',
    token_balance=50
)

# Mentee
mentee1 = CustomUser.objects.create(
    username='charlie@example.com',
    first_name='Charlie',
    last_name='Brown',
    email='charlie@example.com',
    password=make_password('password123'),
    profile_ready=True,
    years_of_experience=1,
    level='junior',
    birth_date=date(2000, 1, 15),
    study_field='Information Technology',
    university='State University',
    linkedin_link='https://linkedin.com/in/charliebrown',
    skills='HTML, CSS, JavaScript basics, Python',
    roles='Junior Developer, CS Student',
    experience='Just graduated, completed one 3-month internship doing basic web dev.',
    summary='Eager to learn backend development and get my first full-time role as a Software Engineer.',
    interests='Gaming, Hackathons, Open Source',
    fun_fact='I can solve a Rubik\'s cube in under a minute.',
    availability_times='Anytime during the week.',
    offerings='My enthusiasm and willingness to learn everything!',
    token_balance=25 # Plenty of tokens to test with
)

# Admin
admin = CustomUser.objects.create_superuser(
    username='admin@example.com',
    email='admin@example.com',
    password='password123'
)
admin.profile_ready = True
admin.first_name = "System"
admin.last_name = "Admin"
admin.years_of_experience = 10
admin.level = 'executive'
admin.birth_date = date(1980, 1, 1)
admin.study_field = 'Management'
admin.university = 'Harvard'
admin.linkedin_link = 'https://linkedin.com/'
admin.save()


print("Creating meetings...")

# PENDING: Charlie requested Alice
m1 = Meeting.objects.create(
    mentee=mentee1,
    mentor=mentor1,
    why_choose_mentor='I want to learn Django from a senior engineer.',
    session_objectives='1. Code review of my side project.\n2. Career advice on getting hired.',
    calendly_link='https://calendly.com/charlie-mentee/30min',
    status='PENDING',
    token_escrowed=1
)
mentee1.token_balance -= 1
mentee1.save()

# ACCEPTED: Charlie requested Bob (Bob accepted)
m2 = Meeting.objects.create(
    mentee=mentee1,
    mentor=mentor2,
    why_choose_mentor='I need help making my React portfolio look professional.',
    session_objectives='Review my resume and React code structure.',
    calendly_link='https://calendly.com/charlie-mentee/45min',
    status='ACCEPTED',
    token_escrowed=5 # 1 initial + 4 on accept
)
mentee1.token_balance -= 5
mentee1.save()

# COMPLETED: Charlie successfully met with Alice before
m3 = Meeting.objects.create(
    mentee=mentee1,
    mentor=mentor1,
    why_choose_mentor='Follow up on our first session.',
    session_objectives='Mock interview for a backend role.',
    calendly_link='https://calendly.com/charlie-mentee/60min',
    status='COMPLETED',
    token_escrowed=0
)

print("Creating evaluations...")

# Add evaluation for completed meeting
Evaluation.objects.create(
    meeting=m3,
    evaluator=mentee1,
    evaluatee=mentor1,
    skills_rating=5,
    experience_rating=5,
    roles_rating=4,
    cv_rating=5,
    interest_rating=5,
    fun_fact_rating=4,
    summary_rating=5,
    comments="Alice is an amazing mentor! Gave me crystal clear feedback on my architecture and really boosted my confidence."
)

print("\n--- SEED COMPLETE ---")
print("Login credentials for testing:")
print(" Mentors: alice@example.com / password123")
print("          bob@example.com / password123")
print(" Mentee:  charlie@example.com / password123")
print(" Admin:   admin@example.com / password123")
