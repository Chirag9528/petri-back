
import inspect
import json
from django.http import HttpRequest, JsonResponse, QueryDict
from app.models import *
from rest_framework.response import Response
from rest_framework.request import Request

from rest_framework.decorators import api_view

from utils import send_error_mail,r200, r500 , send_delete_transaction_mail




def getEventUsers(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        eventid = data.get('eventid')
        
        try:
            event = Event.objects.get(id=eventid)
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Petrichor event not found'}, status=404)
        
        if event.fee == 0:
            participants = EventFreeTable.objects.filter(event=event).values_list('email', flat=True)
        else:
            participants = EventPaidTable.objects.filter(event=event).values_list('email', flat=True)
        
        #Here we will be returning the list of all the participants in the list format 
        return JsonResponse(list(participants), safe=False)



#This is Transaction IDS
#Here i am just iteration through all the transaction ids and marking them true or false or success if that transaction id exists in the req which i will get 
def verifyTR(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Here if no transaction id then it will start with a default of the empty list
        transaction_ids = data.get('transaction_ids', [])
        
        failed_transactions = []

        for transaction_id in transaction_ids:
            try:
                transaction = TransactionTable.objects.get(transaction_id=transaction_id)
                transaction.verified = True
                transaction.save()
            except TransactionTable.DoesNotExist:
                failed_transactions.append(transaction_id)
        
        return JsonResponse({
            'status': 'success',
            'failed_transactions': failed_transactions
        })

@api_view(['GET'])
def unverifTR(request):
    try:
        transaction_ids = []
        transaction = TransactionTable.objects.filter(verified = False)
        for user in transaction:
            transaction_ids.append(user.transaction_id)
        return JsonResponse({
            'status' : 'success',
            'unverified_transactions' : transaction_ids 
        })
    except Exception as e:
        return r500("Opps!! Unable to complete the request!!!")


@api_view(['POST'])
def cancelTR(request):
    try:
        data = json.loads(request.body)
        transaction_notfound = []
        for item in data:
            # Process each JSON object in the array
            transaction_id = item.get('transaction_id')
            email = item.get('email')
            transaction = TransactionTable.objects.get(transaction_id=transaction_id)
            if transaction is not None :
                event_id = transaction.event_id
                event_name = Event.objects.filter(event_id = event_id).name
                transaction.delete()
                send_delete_transaction_mail(email , event_name)
            else:
                transaction_notfound.append(transaction_id)
        if len(transaction_notfound) == 0:
            return JsonResponse({
                'success' : True,
                'message' : 'All mails sent'
            })
        else:
            return JsonResponse({
                'success' : False ,
                'message' : 'Some ids were not found',
                'transaction_notfound' : transaction_notfound
            })
    except TransactionTable.DoesNotExist:
        return JsonResponse({
            'success' : False ,
            'error': 'Transaction not found'
            }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success' : False ,
            'error': 'Invalid JSON'
            }, status=400)




@api_view(['GET'])
def getTR(request):
    try:
        unconfirmed = TransactionTable.objects.filter(verified = False)
        data = []
        for u in unconfirmed:
            if 'test' in u.transaction_id:
                continue
            try:
                event = Event.objects.get(eventId=u.event_id)
                # event = get_event_from_id(u.eventId)
            except Exception as e:
                if u.event_id:
                    print(u.event_id, "doesnt exist")
                continue
            
            emails = u.get_participants()
            if not emails:
                continue
            main_guy = u.user_id
            try:
                main_user = Profile.objects.get(email=main_guy)
                # main_user = get_profile_from_email(main_guy)
            except Exception as e:
                if main_guy:
                    print(main_guy, "doesnt exist")
                continue
            

            data.append({
                'transID': u.transaction_id,
                # 'amount': event.fee,
                'amount': event['fee'],
                'name': main_user.username,
                'phone': main_user.phone,
                'parts': len(emails)
            })
        
        return Response({data},"data fetch successfull")
    except Exception:
        send_error_mail(inspect.stack()[0][3], request.data, e)
        return r500("something bad happened")


@api_view(['GET'])
def unverifTR(request):
    try:
        transaction_ids = []
        transaction = TransactionTable.objects.filter(verified = False)
        for user in transaction:
            transaction_ids.append(user.transaction_id)
        return JsonResponse({
            'status' : 'success',
            'unverified_transactions' : transaction_ids 
        })
    except Exception as e:
        return r500("Opps!! Unable to complete the request!!!")


@api_view(['POST'])
def cancelTR(request):
    try:
        data = json.loads(request.body)
        transaction_notfound = []
        for item in data:
            # Process each JSON object in the array
            transaction_id = item.get('transaction_id')
            email = item.get('email')
            transaction = TransactionTable.objects.get(transaction_id=transaction_id)
            if transaction is not None :
                event_id = transaction.event_id
                event_name = Event.objects.filter(event_id = event_id).name
                transaction.delete()
                send_delete_transaction_mail(email , event_name)
            else:
                transaction_notfound.append(transaction_id)
        if len(transaction_notfound) == 0:
            return JsonResponse({
                'success' : True,
                'message' : 'All mails sent'
            })
        else:
            return JsonResponse({
                'success' : False ,
                'message' : 'Some ids were not found',
                'transaction_notfound' : transaction_notfound
            })
    except TransactionTable.DoesNotExist:
        return JsonResponse({
            'success' : False ,
            'error': 'Transaction not found'
            }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success' : False ,
            'error': 'Invalid JSON'
            }, status=400)




@api_view(['POST'])
def addEvent(request):
    try:
        data=request.data
        if data == None:
            return r500("Please send some info about the event")
        eventId = data.get("event_id" , None)
        if eventId is None:
            return r500("Event Id is missing")
        name = data.get("name" , None)
        if name is None:
            return r500("Event name is missing")
        fee = data.get("fee" , None)
        if fee is None:
            return r500("Event fees is missing")
        minMember = data.get("minMember", None)
        if minMember is None:
            return r500("minMember is missing")
        maxMember = data.get("maxMember" , None)
        if maxMember is None:
            return r500("maxMember is missing")
        isTeam = data.get("isTeam" , None)
        if isTeam is None:
            return r500("isTeam is missing")
        event = Event.objects.create(
            event_id = eventId ,
            name =  name ,
            fee = fee ,
            minMember = minMember ,
            maxMember = maxMember ,
            isTeam = isTeam)
        event.save()
        print('done')
        return r200("Event saved successfully")

    except Exception as e:
        print(e)
        return r500(f'Error: {e}')


@api_view(["POST"])
def updateEvent(request: Request):
    try:
        data=request.data
        if isinstance(data, (dict, QueryDict)):
            print(data)
            dt_eventId = data.get("event_id")
            if dt_eventId is None:
                return r500('Please provide an eventId')
            dt_name=data.get("name")
            dt_fee=data.get("fee")
            dt_minMember=data.get("minMember")
            dt_maxMember=data.get("maxMember")
            dt_isTeam=data.get("isTeam")

            print("wd")
            event = Event.objects.filter(event_id=dt_eventId).first()
            if event is None:
                return r500(f'No event found with eventId {dt_eventId}')
            # print(event.name,event.fee,dt_fee)

            if dt_name is not None and dt_name!= "":
                event.name=dt_name
            if dt_fee is not None:
                event.fee=int(dt_fee)
            if dt_minMember is not None:
                event.minMember=int(dt_minMember)
            if dt_maxMember is not None:
                event.maxMember=int(dt_maxMember)
            if dt_isTeam is not None:
                event.isTeam=bool(dt_isTeam)

            event.save()

            return r200("Event Updated")

    except Exception as e:
        print(e)
        # send_error_mail(inspect.stack()[0][3], request.data, e)
        return r500(f'Error: {e}')

@api_view(['POST'])
def display_sheet(request):
    '''
    Takes in eventID from the request and returns the
    participants of that event in json
    '''
    data = request.data
    eventID = data['id'] if data != None else None
    if eventID:
        return getDataFromID(eventID)

# @lru_cache()
def getDataFromID(eventID):
    try:
        teamlst = TransactionTable.objects.filter(eventId=eventID)
        teamdict = {}  # info of each team
        participants = []  # participants to be added

        for i, team in enumerate(teamlst):
            partis = team.get_participants()
            teamdict['team'] = f"Team{i + 1}"
            teamdict["details"] = []
            for part in partis:
                try:
                    prof = Profile.objects.get(email=part)
                    # prof = get_profile_from_email(part)
                    detail = {
                            "name": f"{prof.username}",
                            "email": f"{part}",
                            "phone": f"{prof.phone}",
                            "CA": f"{team.CACode}",
                            "verified":f"{team.verified}"
                        }
                except Profile.DoesNotExist:
                    detail = {
                            "name": f"not registered",
                            "email": f"{part}",
                            "phone": f"not registered",
                            "CA": f"{team.CACode}",
                            "verified":f"{team.verified}"
                        }
                teamdict["details"].append(detail.copy())

            participants.append(teamdict.copy())

        event = {
                "name": f"{Event.objects.get(eventId=eventID).name}",
                # "name": f"{get_event_from_id(eventID)['name']}",
                "participants": participants
            }

        return Response(event,"Event Data fetched successfully")
    except Exception as e:
        print(e)
        # send_error_mail(inspect.stack()[0][3], request.data, e)
        return r500(f'Error: {e}')
