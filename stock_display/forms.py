from django import forms

class TickerChoiceForm(forms.Form):
    ticker = forms.CharField(
        max_length=10, 
        widget=forms.TextInput(attrs={'name': 'ticker', 'id': 'stock_ticker_text', 'placeholder': 'Enter stock ticker'}),
    )

timeFrameChoices = [
    ('daily', 'Daily'),
    ('monthly', 'Monthly'),
    ('yearly', 'Yearly')
]
    
class TimeFrameForm(forms.Form):
    timeFrame = forms.ChoiceField(
        choices = timeFrameChoices, widget = forms.Select(attrs={'name': 'timeFrame','id': 'timeFrame'})
    )