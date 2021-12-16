from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import Thread, NewMessage
from django.contrib import messages
from django.contrib.auth import logout

# Create your views here.


# def inbox(request):

#     profile = request.user.profile
#     messagesrequest = profile.received_messages.all()
#     unreadMessages = messagesrequest.filter(is_read=False).count()
#     context = {'messagerequest': messagesrequest,
#                'unreadMessages': unreadMessages}
#     return render(request, 'messages.html', context)
def inbox(request):
    threads = (
        Thread.objects.by_user(user=request.user)
        .prefetch_related("thread_id")
        .order_by("timestamp")
    )
    context = {"Threads": threads}

    return render(request, "messages.html", context)

def logoutUser(request):
    logout(request)
    messages.error(request, "User was logged out")
    return redirect("admin:index")
