from django.shortcuts import render, HttpResponse
from .models import TodoItem
import requests
from .forms import TickerChoiceForm
import matplotlib
import matplotlib.pyplot as plt
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
matplotlib.use('agg')

def generate_stock_plot(dates_and_prices):
    fig, ax = plt.subplots()
    ax.plot([item['date'] for item in dates_and_prices], [item['price'] for item in dates_and_prices])
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.set_title('Stock Price Plot')

    canvas = FigureCanvas(fig)
    buffer = io.BytesIO()
    canvas.print_png(buffer)
    plt.close(fig)

    plot_image = buffer.getvalue()

    return plot_image


def home(request):
    dates_and_prices = []
    plot_image = None

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

    else:
        form = TickerChoiceForm()

    return render(request, "home.html", {'form': form, 'dates_and_prices': dates_and_prices, 'plot_image': plot_image})
