from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message
from users.models import User

@login_required
def send_message(request):
    if request.method == 'POST':
        receiver_username = request.POST.get('receiver')
        text = request.POST.get('text')
        receiver = get_object_or_404(User, username=receiver_username)
        Message.objects.create(sender=request.user, receiver=receiver, text=text)
        return redirect('inbox')
    return render(request, 'chat/send_message.html')

@login_required
def inbox(request):
    messages = Message.objects.filter(receiver=request.user)
    return render(request, 'chat/inbox.html', {'messages': messages})