from django import forms

class TickerChoiceForm(forms.Form):
    ticker = forms.CharField(label = 'Stock Ticker')