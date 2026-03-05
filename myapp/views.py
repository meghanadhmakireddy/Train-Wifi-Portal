import random
from django.shortcuts import render, redirect
from .models import TrainPassenger, OTPVerification, ConnectedDevice


# LOGIN VIEW
def login_view(request):
    message = ""

    if request.method == "POST":
        pnr = request.POST.get('pnr')
        mobile = request.POST.get('mobile')

        try:
            TrainPassenger.objects.get(pnr=pnr, journey_active=True)

            otp = str(random.randint(100000, 999999))

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
                    "message": "Device limit reached for this PNR",
                    "otp": request.session.get("otp")
                })

            ConnectedDevice.objects.create(
                pnr=pnr,
                mobile_number=mobile,
                session_id=request.session.session_key
            )

            return redirect("dashboard")

        else:

            return render(request, "otp.html", {
                "message": "Invalid OTP",
                "otp": request.session.get("otp")
            })

    return render(request, "otp.html", {
        "otp": request.session.get("otp")
    })


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