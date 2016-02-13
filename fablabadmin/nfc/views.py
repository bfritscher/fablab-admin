from django.http import HttpResponse
from .models import Token, LogEntry
import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def record_log_entry(request):

    if request.GET.get('id', False):
        token, created = Token.objects.get_or_create(id=request.GET['id'])
        log = LogEntry(token=token, owner=token.owner,
                       payload=json.dumps({'GET': request.GET,
                                           'POST': request.POST,
                                           'BODY': request.body}))
        log.save()

        if token.owner:
            return HttpResponse(u"Hello %d" % token.owner.id)

    return HttpResponse(u"Carte Inconnue") #todo change arduino api to repsect http codes...