from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from .models import CustomUser, Meeting, Evaluation
from .views import request_meeting, meeting_action

class MentorshipFlowTest(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.mentor = CustomUser.objects.create_user(
            username='mentor@test.com', 
            email='mentor@test.com', 
            password='pass', 
            profile_ready=True, 
            token_balance=0,
            first_name='Mentor'
        )
        self.mentee = CustomUser.objects.create_user(
            username='mentee@test.com', 
            email='mentee@test.com', 
            password='pass', 
            profile_ready=True, 
            token_balance=10,
            first_name='Mentee'
        )

    def _setup_request(self, request, user):
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        request.user = user
        request.META['HTTP_REFERER'] = '/'
        return request

    def test_complete_mentorship_lifecycle(self):
        # 1. Request Meeting
        url = reverse('request_meeting', args=[self.mentor.id])
        request = self.rf.post(url, {
            'why_choose_mentor': 'Test Reason',
            'session_objectives': 'Test Objectives',
            'calendly_link': 'http://calendly.com/test'
        })
        self._setup_request(request, self.mentee)
        
        request_meeting(request, self.mentor.id)
        
        self.mentee.refresh_from_db()
        meeting = Meeting.objects.get(mentee=self.mentee, mentor=self.mentor)
        
        self.assertEqual(meeting.status, 'PENDING')
        self.assertEqual(self.mentee.token_balance, 9)
        self.assertEqual(meeting.token_escrowed, 1)

        # 2. Accept Meeting
        url = reverse('meeting_action', args=[meeting.id, 'accept'])
        request = self.rf.get(url)
        self._setup_request(request, self.mentor)
        
        meeting_action(request, meeting.id, 'accept')
        
        self.mentee.refresh_from_db()
        meeting.refresh_from_db()
        
        self.assertEqual(meeting.status, 'ACCEPTED')
        self.assertEqual(self.mentee.token_balance, 5)
        self.assertEqual(meeting.token_escrowed, 5)

        # 3. Complete Meeting
        url = reverse('meeting_action', args=[meeting.id, 'complete'])
        request = self.rf.get(url)
        self._setup_request(request, self.mentor)
        
        meeting_action(request, meeting.id, 'complete')
        
        self.mentor.refresh_from_db()
        meeting.refresh_from_db()
        
        self.assertEqual(meeting.status, 'COMPLETED')
        self.assertEqual(self.mentor.token_balance, 5)
        self.assertEqual(meeting.token_escrowed, 0)
