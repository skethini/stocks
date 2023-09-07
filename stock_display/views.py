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
    plt.savefig(buffer, format = 'png', bbox_inches = 'tight')  # Save the plot to the buffer
    buffer.seek(0)  
    plot_image = buffer.getvalue()  # Get the image data as bytes
    plt.close(fig)

    return plot_image



def home(request):
    dates_and_prices = []
    plot_image_base64 = None

    if request.method == "POST":
        form = TickerChoiceForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data['ticker']
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey=MNNSBHQUZBZUG9FC"
            response = requests.get(url)
            data = response.json()
            data = data["Time Series (Daily)"]

            for date, daily_data in data.items():
                opening_price = float(daily_data["1. open"])  
                dates_and_prices.append({'date': date, 'price': opening_price})
            
            dates_and_prices = dates_and_prices[::-1]

            plot_image = generate_stock_plot(dates_and_prices)
            plot_image_base64 = base64.b64encode(plot_image).decode('utf-8')
            print(plot_image_base64)

    else:
        form = TickerChoiceForm()

    return render(request, "home.html", {'form': form, 'dates_and_prices': dates_and_prices, 'plot_image': plot_image_base64})
