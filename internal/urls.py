from django.urls import path
from . import views

urlpatterns = [
    path('verifyTR/',views.verifyTR,name="verifyTR"),  # under progress   get a list of TRs and verify them Zeeshan
    path('unvertrid/',views.unverifTR,name="unvertrid"), # get a list of TRs and unverify them Zeeshan
    # path('events/unconfirmed',views.getUnconfirmed ,name="unconfirmed"),  # new needed
    path('event/',views.get_event_data,name="getEvent"), 
    path('event/getNextId/',views.get_next_id,name="getEvent"), 
    path('events/add/',views.addEvent,name="addEvent"),
    path('events/update/',views.updateEvent,name="updateEvent"),
    path('events/all/',views.allEvents,name="getAllEvent"),
    path('sheets/view/', views.display_sheet, name="display_sheet"),
    path('sheets/users/',views.getAllUsers,name="get_users")
    # path('unverifTR',views.unverifTR , name="unverifTR"),
    # path('cancelTR',views.cancelTR , name="cancelTR")
]