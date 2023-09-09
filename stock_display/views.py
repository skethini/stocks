from django.shortcuts import render, HttpResponse
from .models import TodoItem
import requests
from .forms import TickerChoiceForm
import matplotlib
import matplotlib.pyplot as plt
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import base64
import matplotlib.ticker as ticker
from django.http import JsonResponse
matplotlib.use('agg')

def autocomplete_ticker(request):
    print("hey")
    query = request.GET.get('term', '')
    print("query ",query)
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
    
    print("results: ",results)
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
        form = TickerChoiceForm(request.POST)
        print('LOOK HERE: ',request.POST.get('ticker', ''))
        if form.is_valid():
            ticker = form.cleaned_data['ticker']
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey=MNNSBHQUZBZUG9FC"
            try:
                print("THIS IS AN intrystatement")
                response = requests.get(url)
                if response.status_code == 200:
                    print("THIS IS AN validstatus")
                    data = response.json()
                    data = data["Time Series (Daily)"]
                    for date, daily_data in data.items():
                        opening_price = float(daily_data["4. close"])  
                        dates_and_prices.append({'date': date, 'price': opening_price})
                    
                    dates_and_prices = dates_and_prices[::-1]

                    plot_image = generate_stock_plot(dates_and_prices)
                    plot_image_base64 = base64.b64encode(plot_image).decode('utf-8')
                    
                else:
                    print("THIS IS AN invalid status")
                    data = []
                    invalidTicker = True
            except:
                print("THIS IS AN inexceptstatement")
                data = []
                invalidTicker = True
        else:
            invalidTicker = True
            print("THIS IS FORMINVALID")

    else:
        print("THIS IS AN else")
        form = TickerChoiceForm()

    print("invalidTicker:", invalidTicker)
    context = {'form': form, 'dates_and_prices': dates_and_prices, 'plot_image': plot_image_base64, 'invalidTicker': invalidTicker}

    return render(request, "home.html", context)
