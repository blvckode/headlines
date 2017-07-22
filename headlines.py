from flask import Flask ,render_template ,request, make_response
import datetime
import feedparser
import json
import urllib2
import urllib


app = Flask(__name__)


RSS_FEEDS = {'bbc':'http://feeds.bbci.co.uk/news/rss.xml',
'cnn':'http://rss.cnn.com/rss/edition.rss',
'fox':'http://feeds.foxnews.com/foxnews/latest',
'iol':'http://www.iol.co.za/cmlink/1.640'}

weather_api_url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=1210c5195cd16a94f2ebd7946d12c471'
currency_api_url = "https://openexchangerates.org//api/latest.json?app_id=42f428d203e4415ba9a51728ab57b83a"

DEFAULTS = {'publication':'bbc','city':'London,UK','currency_from':'GBP',
            'currency_to':'USD'}

def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]

@app.route("/")
def home():
    # get customised publication based on user input or default
    publication = get_value_with_fallback("publication")
    articles = get_news(publication)

    # get customised weather based on user input or default
    city = get_value_with_fallback('city')
    weather = get_weather(city)

    # get customised currency based on user input or default
    currency_from = get_value_with_fallback('currency_from')
    currency_to = get_value_with_fallback('currency_to')
    rate, currencies = get_rate(currency_from, currency_to)

    # save cookies and return template
    response = make_response(render_template("home.html",publication = publication,  articles = articles,weather=weather, currency_from = currency_from,
                           currency_to = currency_to, rate = rate, currencies = sorted(currencies)))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)
    return response

def get_rate(frm, to):
    all_currency = urllib2.urlopen(currency_api_url).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate / frm_rate, parsed.keys())

def get_news(publication):
    feed = feedparser.parse(RSS_FEEDS[publication.lower()])
    return feed['entries']

def get_weather(query):
    query = urllib.quote(query)
    url = weather_api_url.format(query)
    data = urllib2.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {"description":parsed["weather"][0]["description"],"temperature":parsed["main"]["temp"],
                   "city":parsed["name"],"country":parsed["sys"]["country"]}
    return weather






if __name__ == "__main__":
    app.run(debug=True)