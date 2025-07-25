from django import forms

INSURANCE_CHOICES = [
    ('Medicare', 'Medicare'),
    ('Cigna', 'Cigna'),
    ('Aetna', 'Aetna'),
    ('BCBS', 'Blue Cross Blue Shield'),
    ('Humana', 'Humana'),
    # add more insurers here if you like
]

NECESSITY_CHOICES = [
    ('ALS', 'Advanced Life Support'),
    ('BLS', 'Basic Life Support'),
    ('Stretcher', 'Stretcher'),
    ('Wheelchair', 'Wheelchair'),
    ('None', 'No medical necessity'),
]

class TransportRequestForm(forms.Form):
    pickup_location = forms.CharField(label="Pickup Location")
    dropoff_location = forms.CharField(label="Drop‑off Location")
    insurance_provider = forms.ChoiceField(choices=INSURANCE_CHOICES)
    medical_necessity = forms.ChoiceField(choices=NECESSITY_CHOICES)
