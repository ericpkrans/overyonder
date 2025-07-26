from django.shortcuts import render, get_object_or_404
from .forms import TransportRequestForm
from .models import TransportVendor, AuditLog


# ─────────────────────────────────────────────────────────────
# Request form + vendor list
# ─────────────────────────────────────────────────────────────
def request_transport(request):
    if request.method == "POST":
        form = TransportRequestForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # ── Medicare branch: audit + link to Modivcare ────────────────
            if data["insurance_provider"] == "Medicare":
                AuditLog.objects.create(
                    pickup_location=data.get("pickup_location", "N/A"),
                    dropoff_location=data.get("dropoff_location", "N/A"),
                    insurance_provider="Medicare",
                    medical_necessity=data.get("medical_necessity", "N/A"),
                    vendor_selected=None,
                    justification="Redirected to Modivcare",
                )
                return render(
                    request,
                    "thank_you.html",
                    {
                        "medicare": True,
                        "modiv_url": "https://member.modivcare.com",
                    },
                )

            # Save data in session for later logging
            request.session["request_data"] = data

            # ── No medical necessity → Uber / Lyft fallback ──────────────
            if data["medical_necessity"] == "None":
                ul_qs = TransportVendor.objects.filter(
                    name__in=["Uber", "Lyft"]
                ).values("id", "name", "price", "eta")

                if ul_qs.exists():
                    vendors = list(ul_qs)
                else:
                    vendors = [
                        {"id": 0, "name": "Uber", "price": "Market rate", "eta": "<15 min"},
                        {"id": 0, "name": "Lyft", "price": "Market rate", "eta": "<15 min"},
                    ]
            else:
                # Default: 3 cheapest in DB
                vendors = list(
                    TransportVendor.objects.all()
                    .order_by("price")
                    .values("id", "name", "price", "eta")[:3]
                )

            return render(request, "results.html", {"vendors": vendors, "data": data})

    # GET → show blank form
    form = TransportRequestForm()
    return render(request, "request_form.html", {"form": form})


# ─────────────────────────────────────────────────────────────
# Selecting a vendor (real or fallback)
# ─────────────────────────────────────────────────────────────
def select_vendor(request, vendor_id):
    """
    Handles:
      • Real vendors (id > 0)
      • Uber/Lyft fallback (id == 0)
    """

    # ── Fallback: Uber / Lyft row (id == 0) ─────────────────────────────
    if vendor_id == 0:
        data = request.session.get("request_data", {})
        chosen_name = request.GET.get("name", "Uber/Lyft")

        AuditLog.objects.create(
            pickup_location=data.get("pickup_location", "N/A"),
            dropoff_location=data.get("dropoff_location", "N/A"),
            insurance_provider=data.get("insurance_provider", "N/A"),
            medical_necessity=data.get("medical_necessity", "N/A"),
            vendor_selected=None,
            justification=f"Booked via {chosen_name}",
        )
        return render(request, "thank_you.html", {"vendor_name": chosen_name})

    # ── Normal vendors (id > 0) ─────────────────────────────────────────
    vendor = get_object_or_404(TransportVendor, id=vendor_id)
    cheapest_price = TransportVendor.objects.order_by("price").first().price
    data = request.session.get("request_data", {})

    # POST ⇒ justification submitted
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

    # GET ⇒ ask for justification if not cheapest
    if vendor.price > cheapest_price:
        return render(request, "justify.html", {"vendor": vendor})

    # Cheapest ⇒ auto‑log
    AuditLog.objects.create(
        pickup_location=data.get("pickup_location", "N/A"),
        dropoff_location=data.get("dropoff_location", "N/A"),
        insurance_provider=data.get("insurance_provider", "N/A"),
        medical_necessity=data.get("medical_necessity", "N/A"),
        vendor_selected=vendor,
        justification="",
    )
    return render(request, "thank_you.html", {"vendor": vendor})
