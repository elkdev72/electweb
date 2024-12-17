import requests, base64, json, re, os
from datetime import datetime
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Transaction
from .forms import PaymentForm
from dotenv import load_dotenv

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


# Load environment variables
load_dotenv()
print("MPESA_BASE_URL:", os.getenv("MPESA_BASE_URL"))

# Retrieve variables from the environment
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")

MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE")
CALLBACK_URL = os.getenv("CALLBACK_URL")
MPESA_BASE_URL = os.getenv("MPESA_BASE_URL")

# Phone number formatting and validation
def format_phone_number(phone):
    phone = phone.replace("+", "")
    if re.match(r"^254\d{9}$", phone):
        return phone
    elif phone.startswith("0") and len(phone) == 10:
        return "254" + phone[1:]
    else:
        raise ValueError("Invalid phone number format")

# Generate M-Pesa access token
import base64

CONSUMER_KEY = "pCtOCqrzmENqLUnU5HaB9sjVeofWX02jdGM5zetJQR2OqcK3"
CONSUMER_SECRET = "2J88b9zIVx1Gnw1svoIIil72t60WuQNJiHDGi7l9SGfjZiInA8KOHTsGJhGpiGmb"

def generate_access_token():
    try:
        # Step 1: Prepare credentials
        credentials = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"
        
        # Step 2: Properly encode the credentials into base64
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        # Debug: print encoded credentials to check correctness
        print("Encoded Credentials:", encoded_credentials)

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
        }

        # Debug: print headers to verify
        print("Request Headers:", headers)

        response = requests.get(
            f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials",
            headers=headers,
        )

        # Debug: print response status and content
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")

        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                return data["access_token"]
            else:
                raise Exception("Access token missing in response.")
        else:
            raise Exception(f"Failed to fetch access token. Status code: {response.status_code}, Response: {response.text}")

    except requests.RequestException as e:
        raise Exception(f"Failed to connect to M-Pesa: {str(e)}")
    except ValueError as e:
        raise Exception(f"Error parsing the response: {str(e)}")

# Testing the function directly
try:
    token = generate_access_token()
    print("Access Token:", token)
except Exception as e:
    print("Error:", str(e))



# Initiate STK Push and handle response







def initiate_stk_push(phone, amount):
    try:
        # Step 1: Generate access token
        token = generate_access_token()

        # Step 2: Prepare the headers for the STK Push request
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

        # Step 3: Prepare the request body for STK Push
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        stk_password = base64.b64encode(
            (MPESA_SHORTCODE + MPESA_PASSKEY + timestamp).encode()
        ).decode()

        request_body = {
            "BusinessShortCode": MPESA_SHORTCODE,  # Your M-Pesa shortcode
            "Password": stk_password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",  # Use CustomerPayBillOnline or CustomerBuyGoodsOnline
            "Amount": amount,
            "PartyA": phone,  # PartyA is the phone number of the payer
            "PartyB": MPESA_SHORTCODE,  # PartyB is your M-Pesa shortcode
            "PhoneNumber": phone,
            "CallBackURL": CALLBACK_URL,  # Replace with your callback URL
            "AccountReference": "account",  # Optional reference for the transaction
            "TransactionDesc": "Payment for goods",  # Description of the transaction
        }

        # Step 4: Send the request
        response = requests.post(
            f"{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest",
            json=request_body,
            headers=headers,
        )

        # Step 5: Handle the response
        if response.status_code == 200:
            data = response.json()
            if "ResponseCode" in data and data["ResponseCode"] == "0":
                # Success response, STK Push initiated successfully
                print("STK Push initiated successfully.")
                return data
            else:
                # Error response from M-Pesa
                error_message = data.get("errorMessage", "Unknown error")
                raise Exception(f"Error from M-Pesa: {error_message}")
        else:
            raise Exception(f"Failed to initiate STK Push. Status code: {response.status_code}, Response: {response.text}")

    except requests.RequestException as e:
        print(f"Error connecting to M-Pesa: {str(e)}")
        return {"errorMessage": f"Error connecting to M-Pesa: {str(e)}"}
    except Exception as e:
        print(f"Error initiating STK Push: {str(e)}")
        return {"errorMessage": str(e)}





# Payment View
def payment_view(request):
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            try:
                phone = format_phone_number(form.cleaned_data["phone_number"])
                amount = form.cleaned_data["amount"]
                response = initiate_stk_push(phone, amount)
                print(response)

                if response.get("ResponseCode") == "0":
                    checkout_request_id = response["CheckoutRequestID"]
                    return render(request, "pending.html", {"checkout_request_id": checkout_request_id})
                else:
                    error_message = response.get("errorMessage", "Failed to send STK push. Please try again.")
                    return render(request, "payment_form.html", {"form": form, "error_message": error_message})

            except ValueError as e:
                return render(request, "payment_form.html", {"form": form, "error_message": str(e)})
            except Exception as e:
                return render(request, "payment_form.html", {"form": form, "error_message": f"An unexpected error occurred: {str(e)}"})

    else:
        form = PaymentForm()

    return render(request, "payment_form.html", {"form": form})

# Query STK Push status
def query_stk_push(checkout_request_id):
    print("Querying STK Push status...")
    try:
        token = generate_access_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            (MPESA_SHORTCODE + MPESA_PASSKEY + timestamp).encode()
        ).decode()

        request_body = {
            "BusinessShortCode": MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }

        response = requests.post(
            f"{MPESA_BASE_URL}/mpesa/stkpushquery/v1/query",
            json=request_body,
            headers=headers,
        )

        print(f"STK Query Response Status Code: {response.status_code}")
        print(f"STK Query Response Body: {response.text}")

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to query STK Push. Status Code: {response.status_code}, Response: {response.text}")

    except requests.RequestException as e:
        print(f"Error querying STK status: {str(e)}")
        return {"error": str(e)}

# View to query the STK status and return it to the frontend
def stk_status_view(request):
    if request.method == 'POST':
        try:
            # Parse the JSON body
            data = json.loads(request.body)
            checkout_request_id = data.get('checkout_request_id')
            print("CheckoutRequestID:", checkout_request_id)

            # Query the STK push status using your backend function
            status = query_stk_push(checkout_request_id)

            # Return the status as a JSON response
            return JsonResponse({"status": status})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt  # To allow POST requests from external sources like M-Pesa
def payment_callback(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST requests are allowed")

    try:
        callback_data = json.loads(request.body)  # Parse the request body
        result_code = callback_data["Body"]["stkCallback"]["ResultCode"]

        if result_code == 0:
            # Successful transaction
            checkout_id = callback_data["Body"]["stkCallback"]["CheckoutRequestID"]
            metadata = callback_data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]

            amount = next(item["Value"] for item in metadata if item["Name"] == "Amount")
            mpesa_code = next(item["Value"] for item in metadata if item["Name"] == "MpesaReceiptNumber")
            phone = next(item["Value"] for item in metadata if item["Name"] == "PhoneNumber")

            # Save transaction to the database
            Transaction.objects.create(
                amount=amount, 
                checkout_id=checkout_id, 
                mpesa_code=mpesa_code, 
                phone_number=phone, 
                status="Success"
            )
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Payment successful"})

        # Payment failed
        return JsonResponse({"ResultCode": result_code, "ResultDesc": "Payment failed"})

    except (json.JSONDecodeError, KeyError) as e:
        return HttpResponseBadRequest(f"Invalid request data: {str(e)}")

print("M-Pesa Access Token URL:", f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials")
# Check if the environment variables are being loaded correctly
print(f"MPESA_CONSUMER_KEY: {os.getenv('MPESA_CONSUMER_KEY')}")
print(f"MPESA_CONSUMER_SECRET: {os.getenv('MPESA_CONSUMER_SECRET')}")
print(f"MPESA_BASE_URL: {os.getenv('MPESA_BASE_URL')}")
