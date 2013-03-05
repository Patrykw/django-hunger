from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from hunger.models import InvitationCode, Invitation
from hunger.forms import InviteSendForm
from hunger.utils import setting, now
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.http import HttpResponse
from django.contrib.auth.models import User


class NotBetaView(TemplateView):
    """
    Display a message to the user after the invite request is completed
    successfully.
    """
    template_name='hunger/not_in_beta.html'


class VerifiedView(TemplateView):
    """
    Display a message to the user after the invite request is completed
    successfully.
    """
    template_name='hunger/verified.html'


class InvalidView(TemplateView):
    """
    Display a message to the user that the invitation code is
    invalid or has already been used.
    """
    template_name='hunger/invalid.html'


def verify_invite(request, code):
    response = redirect(setting('HUNGER_VERIFIED_REDIRECT'))
    response.set_cookie('hunger_code', code)
    return response
    
def invite_email(request):
    email = request.POST['email']
    code = InvitationCode.objects.filter(owner=request.user)
    if code:
        code = code[0]
        if code.num_invites > 0:
            user = User.objects.filter(email=email)
            if user:
                user = user[0]
                inv = Invitation.objects.filter(user=user)
                if inv:
                    inv = inv[0]
                    if not inv.invited:
                        inv.invited = now()
                        inv.save()
                        code.num_invites -= 1
                        code.save()
            else:
                right_now = now()
                inv = Invitation(email=email, invited=right_now, created=right_now)
                inv.save()
                code.num_invites -= 1
                code.save()
            return HttpResponse("Invited!")    
    return HttpResponse("Not invited!")
