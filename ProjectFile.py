import requests
import time
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from textblob import TextBlob
import spacy
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
api_key = os.getenv('NYT_API_KEY')

def fetch_articles_for_date(year, month, day, api_key):
    """Fetch articles for a specific date."""
    articles = []
    page = 0
    while True:
        url = (
            f"https://api.nytimes.com/svc/search/v2/articlesearch.json"
            f"?q=Israel"
            f"&fq=glocations:(\"Gaza Strip\")"
            f"&begin_date={year}{month:02d}{day:02d}"
            f"&end_date={year}{month:02d}{day:02d}"
            f"&api-key={api_key}"
            f"&page={page}"
        )
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for doc in data['response']['docs']:
                headline = doc['headline']['main']
                pub_date = doc['pub_date']
                formatted_pub_date = pub_date.replace('T', ' ').split('+')[0]
                articles.append(f"{headline} | Published on: {formatted_pub_date}")
            if not data['response']['docs']:
                break
            page += 1
        elif response.status_code == 429:
            print("Rate limit exceeded. Waiting before retrying...")
            time.sleep(60)
        else:
            print(f"Error fetching data for {year}-{month}-{day}: {response.status_code}")
            break
    return articles

def fetch_articles_for_period(start_year, start_month, end_year, end_month, api_key):
    """Fetch articles for a specified period."""
    articles = []
    start_date = datetime(start_year, start_month, 1)
    end_date = datetime(end_year, end_month, get_last_day_of_month(end_year, end_month))
    current_date = start_date
    while current_date <= end_date:
        articles.extend(fetch_articles_for_date(current_date.year, current_date.month, current_date.day, api_key))
        current_date += timedelta(weeks=1)
    return articles

def get_last_day_of_month(year, month):
    """Get the last day of the month."""
    return (
        31 if month in [1, 3, 5, 7, 8, 10, 12]
        else 30 if month != 2
        else 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        else 28
    )

def prepare_dataframe(articles):
    """Prepare a DataFrame from the list of articles."""
    df_articles = pd.DataFrame(articles, columns=['article_info'])
    split_df = df_articles['article_info'].str.split(r' \| Published on: ', expand=True)
    df_articles[['headline', 'pub_info']] = split_df
    df_articles[['pub_date', 'pub_time']] = df_articles['pub_info'].str.split(' ', expand=True)
    df_articles['pub_date'] = pd.to_datetime(df_articles['pub_date'])
    df_articles.drop(['article_info', 'pub_info'], axis=1, inplace=True)
    return df_articles

def get_sentiment(text):
    """Get sentiment polarity."""
    return TextBlob(text).sentiment.polarity

def analyze_sentiment(df):
    """Analyze sentiment and prepare weekly sentiment data."""
    df['sentiment'] = df['headline'].apply(get_sentiment)
    nlp = spacy.load('en_core_web_sm')
    df.set_index('pub_date', inplace=True)
    weekly_sentiment = df.resample('W-SUN')['sentiment'].mean().reset_index()
    return weekly_sentiment

def plot_sentiment(weekly_sentiment):
    """Plot weekly sentiment data."""
    x = weekly_sentiment['pub_date'].tolist()
    y = weekly_sentiment['sentiment'].tolist()
    plt.figure(figsize=(15, 8))
    plt.plot(x, y, marker='o', linestyle='-')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
    plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.SUNDAY))
    plt.gcf().autofmt_xdate()
    plt.title('Weekly Average Sentiment')
    plt.xlabel('Date (Week Starting From)')
    plt.ylabel('Average Sentiment')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    # Fetch articles
    key_date_articles = fetch_articles_for_date(2023, 10, 7, api_key)
    period_articles = fetch_articles_for_period(2023, 9, 2024, 1, api_key)
    combined_articles = key_date_articles + period_articles
    
    # Prepare DataFrame
    df_articles = prepare_dataframe(combined_articles)
    df_articles_sorted = df_articles.sort_values(by=['pub_date', 'pub_time'])
    df_articles_sorted.to_csv('sorted_articles.csv', index=False)
    
    # Load and filter data
    df = pd.read_csv('sorted_articles.csv')
    df['pub_date'] = pd.to_datetime(df['pub_date'])
    df = df[(df['pub_date'] >= '2023-10-07') & (df['pub_date'] <= '2024-01-26')]
    
    # Analyze sentiment
    weekly_sentiment = analyze_sentiment(df)
    
    # Plot sentiment
    plot_sentiment(weekly_sentiment)

if __name__ == "__main__":
    main()

