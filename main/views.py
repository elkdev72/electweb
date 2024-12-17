from django.shortcuts import render
from django.core.mail import send_mail, EmailMessage

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == "POST":
        message_name = request.POST['message-name']
        message_email = request.POST['message-email']
        message_subject = request.POST['message-subject']
        unmessage = request.POST['usermessage']

        email = EmailMessage(
            subject=f"{message_subject} ",
            body=unmessage,
            from_email=settings.EMAIL_HOST_USER,
            to=[settings.EMAIL_HOST_USER],
            reply_to=[message_email]
        )
        email.send()
        return redirect('/messagesent/')
    else:
        return render(request, template_name="contact.html")



def services(request):
    return render(request, 'service.html')

def projects(request):
    return render(request, 'project.html')

def blog(request):
    return render(request, 'blog.html')

def team(request):
    return render(request, 'team.html')

def testimonials(request):
    return render(request, 'testimonial.html')
