from django.shortcuts import render, get_object_or_404
from .forms import TransportRequestForm
from .models import TransportVendor, AuditLog


def request_transport(request):
    if request.method == "POST":
        form = TransportRequestForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Medicare redirect
            if data["insurance_provider"] == "Medicare":
                return render(request, "thank_you.html", {"medicare": True})

            # Store form data for later logging
            request.session["request_data"] = data

            # --- New logic: if no medical necessity, suggest Uber/Lyft ---
            if data["medical_necessity"] == "None":
                vendors = [
                    {"name": "Uber", "price": "Market rate", "eta": "≈ <15 min"},
                    {"name": "Lyft", "price": "Market rate", "eta": "≈ <15 min"},
                ]
            else:
                # Default: 3 cheapest medical vendors from the DB
                vendors = list(
                    TransportVendor.objects.all()
                    .order_by("price")
                    .values("name", "price", "eta")[:3]
                )

            return render(request, "results.html", {"vendors": vendors, "data": data})

    # GET request – show blank form
    form = TransportRequestForm()
    return render(request, "request_form.html", {"form": form})


def select_vendor(request, vendor_id):
    vendor = get_object_or_404(TransportVendor, id=vendor_id)
    cheapest_price = (
        TransportVendor.objects.order_by("price").first().price
    )  # cheapest in DB

    # Retrieve original request data
    data = request.session.get("request_data", {})

    # ----- If POST: justification submitted -----
    if request.method == "POST":
        reason = request.POST.get("reason", "")

        AuditLog.objects.create(
            pickup_location=data.get("pickup_location", "N/A"),
            dropoff_location=data.get("dropoff_location", "N/A"),
            insurance_provider=data.get("insurance_provider", "N/A"),
            medical_necessity=data.get("medical_necessity", "N/A"),
            vendor_selected=vendor,
            justification=reason,
        )

        return render(request, "thank_you.html", {"vendor": vendor, "reason": reason})

    # ----- If GET: deciding which page to show -----
    if vendor.price > cheapest_price:
        # More expensive → ask for justification
        return render(request, "justify.html", {"vendor": vendor})

        # Cheapest choice → save immediately with empty justification
    AuditLog.objects.create(
        pickup_location=data.get("pickup_location", "N/A"),
        dropoff_location=data.get("dropoff_location", "N/A"),
        insurance_provider=data.get("insurance_provider", "N/A"),
        medical_necessity=data.get("medical_necessity", "N/A"),
        vendor_selected=vendor,
        justification="",
    )

    return render(request, "thank_you.html", {"vendor": vendor})
