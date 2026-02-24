import random
from django.shortcuts import render, redirect
from .models import TrainPassenger, OTPVerification

import random
from django.shortcuts import render, redirect
from .models import TrainPassenger, OTPVerification

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
            request.session['otp'] = otp   # ← add this line

            return redirect('verify_otp')

        except TrainPassenger.DoesNotExist:
            message = "Invalid or inactive PNR"

    return render(request, "login.html", {"message": message})


def verify_otp(request):
    message = ""
    otp_display = request.session.get('otp')

    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        mobile = request.session.get('mobile')

        try:
            OTPVerification.objects.filter(
                mobile_number=mobile,
                otp=entered_otp
            ).latest('created_at')

            message = "OTP Verified. Connected Successfully."

        except:
            message = "Invalid OTP"

    return render(request, "otp.html", {
        "message": message,
        "otp": otp_display
    })