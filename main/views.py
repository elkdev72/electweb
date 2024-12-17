from django.shortcuts import render,redirect
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.contrib import messages

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')




def contact(request):
    if request.method == "POST":
        try:
            message_name = request.POST['message-name']
            message_email = request.POST['message-email']
            message_subject = request.POST['message-subject']
            unmessage = request.POST['usermessage']

            email = EmailMessage(
                subject=message_subject,
                body=f"Message from {message_name} ({message_email}):\n\n{unmessage}",
                from_email=settings.EMAIL_HOST_USER,
                to=[settings.EMAIL_HOST_USER],
                reply_to=[message_email]
            )
            email.send(fail_silently=False)
            messages.success(request, "Your message has been sent successfully!")
            return redirect('message_sent')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('contact')
    else:
        return render(request, "contact.html")




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

def message_sent(request):
    return render(request, 'message_sent.html')