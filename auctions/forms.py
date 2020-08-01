from django import forms
from django.forms import ModelForm
from .models import Listing, Bid


class ListingForm(ModelForm):
    image_url = forms.URLField(required=False)
    category = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Listing
        fields = ['title', 'description', 'price',
                  'image_url', 'category']


class BidForm(ModelForm):
    price = forms.FloatField(label='', widget=forms.TextInput(
        attrs={'placeholder': 'Bid'}))

    class Meta:
        model = Bid
        fields = ['price']
