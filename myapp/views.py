from django.shortcuts import render
from .models import TrainPassenger

def login_view(request):
    message = ""

    if request.method == "POST":
        pnr = request.POST.get('pnr')
        mobile = request.POST.get('mobile')  # passenger mobile for OTP later

        try:
            passenger = TrainPassenger.objects.get(
                pnr=pnr,
                journey_active=True
            )
            message = "PNR Verified. OTP will be sent to your number."
        except TrainPassenger.DoesNotExist:
            message = "Invalid or inactive PNR"

    return render(request, "login.html", {"message": message})