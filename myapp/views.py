import random
from django.shortcuts import render, redirect
from .models import TrainPassenger, OTPVerification, ConnectedDevice

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException


import os

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


# LOGIN VIEW
# LOGIN VIEW
def login_view(request):

    message = ""

    if request.method == "POST":

        pnr = request.POST.get('pnr')
        mobile = request.POST.get('mobile')

        # ---------- INPUT VALIDATION (NEW) ----------

        if not pnr.isdigit() or len(pnr) != 10:
            return render(request, "login.html", {
                "message": "Enter a valid 10-digit PNR number."
            })

        if not mobile.isdigit() or len(mobile) != 10:
            return render(request, "login.html", {
                "message": "Enter a valid 10-digit mobile number."
            })

        # ---------- EXISTING LOGIC CONTINUES ----------

        try:
            TrainPassenger.objects.get(pnr=pnr, journey_active=True)

            otp = str(random.randint(100000, 999999))

            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

            try:
                client.messages.create(
                    body=f"Your Train WiFi OTP is {otp}",
                    from_=TWILIO_PHONE_NUMBER,
                    to="+91" + mobile
                )

            except TwilioRestException:
                return render(request, "login.html", {
                    "message": "This number cannot receive OTP as it is not verified. Please use a verified number."
                })

            OTPVerification.objects.create(
                mobile_number=mobile,
                otp=otp
            )

            request.session['mobile'] = mobile
            request.session['otp'] = otp
            request.session['pnr'] = pnr

            return redirect('verify_otp')

        except TrainPassenger.DoesNotExist:

            message = "Invalid or inactive PNR"

    return render(request, "login.html", {"message": message})


# OTP VERIFICATION
def verify_otp(request):

    if request.method == "POST":

        entered_otp = request.POST.get("otp")
        mobile = request.session.get("mobile")
        pnr = request.session.get("pnr")

        if entered_otp == request.session.get("otp"):

            passenger = TrainPassenger.objects.get(pnr=pnr)

            active_devices = ConnectedDevice.objects.filter(
                pnr=pnr,
                active=True
            ).count()

            if active_devices >= passenger.passenger_count:

                return render(request, "otp.html", {
                    "message": "Device limit reached for this PNR"
                })

            ConnectedDevice.objects.create(
                pnr=pnr,
                mobile_number=mobile,
                session_id=request.session.session_key
            )

            return redirect("dashboard")

        else:

            return render(request, "otp.html", {
                "message": "Invalid OTP"
            })

    return render(request, "otp.html")


# DASHBOARD
def dashboard(request):

    pnr = request.session.get("pnr")

    if not pnr:
        return redirect("login")

    passenger = TrainPassenger.objects.get(pnr=pnr)

    connected = ConnectedDevice.objects.filter(
        pnr=pnr,
        active=True
    ).count()

    return render(request, "dashboard.html", {
        "pnr": pnr,
        "connected": connected,
        "allowed": passenger.passenger_count
    })


# DISCONNECT
def disconnect(request):

    session = request.session.session_key

    device = ConnectedDevice.objects.filter(
        session_id=session,
        active=True
    ).first()

    if device:
        device.active = False
        device.save()

    request.session.flush()

    return redirect("login")