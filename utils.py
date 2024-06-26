
import json
from django.core.mail import send_mail
from django.conf import settings


from app.models import Institute, Profile
from petri_ca import settings
from rest_framework.response import Response 
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from custom.authorizor import PetrichorJWTAuthentication


Refreshserializer = TokenRefreshSerializer()
PetrichorAuthenticator = PetrichorJWTAuthentication()

AUTH_EXEMPT = ['/internal/','/api/register/','/api/login/','/api/forget-password/','/api/change-password']

# Helper functions
def error_response(message):
    return Response({"error": message}, status=500)

def success_response(message):
    return Response({"message": message}, status=200)


def send_error_mail(name, data, e):
    '''
        Sends a mail to website developers
    '''
    if "password" in data.keys():
        data["password"]=""
    send_mail(f'Website Error in: {name}',
                message= f'Exception: {e}\nData: {json.dumps(data)}',
                recipient_list=['112201024@smail.iitpkd.ac.in','112201020@smail.iitpkd.ac.in'],
                from_email=settings.EMAIL_HOST_USER)

def get_profile_data(user_profile:Profile):
    '''
        returns the profile data as a dict
        NOTE- Any None handled error raised by this functions is/must be handled by the caller function.
    '''
    user_data = {}
    user_data['username'] = user_profile.username
    user_data['phone'] = user_profile.phone
    user_data['stream'] = user_profile.stream
    user_data['gradYear'] = user_profile.gradYear
    int_id = user_profile.instituteID
    try:
        institute = Institute.objects.get(pk = int_id)
        institute = institute.instiName
    except Institute.DoesNotExist:
        institute = ""     
    user_data['institute'] = institute
    return user_data
    
def get_profile_events(user_email:str):
    '''
        returns the eventIds of events in which this user has registered
        NOTE- Any None handled error raised by this functions is/must be handled by the caller function.
    '''
    events=[]
    # to be Fixed
    eventEntries=EventTable.objects.all() # type: ignore
    for eventEntry in eventEntries:
        if user_email in eventEntry.get_emails():
            events.append({
                "eventId":eventEntry.eventId,
                "status":eventEntry.verified})
    return events


def method_not_allowed():
    return Response({
            "status":405,
            "message":"Method Not Allowed.Use POST"
        },405)

def send_forget_password_mail(email , token):
    subject = 'Your forget password link'
    message = f'Hi , Click on the link to reset your password http://127.0.0.1:8000/api/change-password/{token}/'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject , message , email_from , recipient_list)
    return True





    