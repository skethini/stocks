from django.shortcuts import render, HttpResponse
import requests
from .forms import TickerChoiceForm
from .forms import TimeFrameForm
import matplotlib
import matplotlib.pyplot as plt
import io
import base64
import matplotlib.ticker as ticker
from django.http import JsonResponse
matplotlib.use('agg')

def autocomplete_ticker(request):
    query = request.GET.get('term', '')
    url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={query}&apikey=MNNSBHQUZBZUG9FC"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            data = data["bestMatches"]
            results = [{'value': item['1. symbol'], 'label': item['2. name']} for item in data]
        else:
            results = []
    except:
        results = []
    
    return JsonResponse(results, safe=False)


def generate_stock_plot(dates_and_prices):
    fig, ax = plt.subplots()
    dates_to_display = dates_and_prices[::15]
    ax.plot([item['date'] for item in dates_and_prices], [item['price'] for item in dates_and_prices])
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.set_title('Stock Price Plot')
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.xticks(rotation = 45)

    buffer = io.BytesIO()  
    plt.savefig(buffer, format = 'png', bbox_inches = 'tight')  
    buffer.seek(0)  
    plot_image = buffer.getvalue()  
    plt.close(fig)

    return plot_image


def home(request):
    dates_and_prices = []
    plot_image_base64 = None
    invalidTicker = False

    if request.method == "POST":
        tickerForm = TickerChoiceForm(request.POST)
        timeFrameForm = TimeFrameForm(request.POST)

        if tickerForm.is_valid() and timeFrameForm.is_valid():
            ticker = tickerForm.cleaned_data['ticker']
            timeFrame =  timeFrameForm.cleaned_data['timeFrame']
            timeFrameUpper = timeFrame.upper()
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_{timeFrameUpper}&symbol={ticker}&apikey=MNNSBHQUZBZUG9FC"
            print(url)

            try:
                response = requests.get(url)
                print(response.status_code)
                if response.status_code == 200:
                    timeFrame = timeFrame.capitalize()
                    string = "Time Series (" + timeFrame + ")"
                    print(string)
                    data = response.json()
                    data = data[string]
                    print("DATA: ",data)
                    for date, timeFrameData in data.items():
                        opening_price = float(timeFrameData["4. close"])  
                        dates_and_prices.append({'date': date, 'price': opening_price})
                    
                    dates_and_prices = dates_and_prices[::-1]

                    plot_image = generate_stock_plot(dates_and_prices)
                    plot_image_base64 = base64.b64encode(plot_image).decode('utf-8')
                    
                else:
                    data = []
                    invalidTicker = True
            except:
                print("EXCEPT")
                data = []
                invalidTicker = True
        else:
            invalidTicker = True

    else:
        tickerForm = TickerChoiceForm()
        timeFrameForm = TimeFrameForm()

    context = {'timeFrameForm': timeFrameForm, 'tickerForm': tickerForm, 'dates_and_prices': dates_and_prices, 'plot_image': plot_image_base64, 'invalidTicker': invalidTicker}

    return render(request, "home.html", context)
