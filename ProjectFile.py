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

# Define a function to fetch articles for a specific date
def fetch_articles_for_date(year, month, day, api_key):
    articles = []  # Initialize an empty list to store articles
    page = 0  # Start fetching from the first page
    while True:  # Continue fetching until there are no more articles
        # Construct the URL with specified parameters
        url = (
            f"https://api.nytimes.com/svc/search/v2/articlesearch.json"
            f"?q=Israel"
            f"&fq=glocations:(\"Gaza Strip\")"
            f"&begin_date={year}{month:02d}{day:02d}"
            f"&end_date={year}{month:02d}{day:02d}"
            f"&api-key={api_key}"
            f"&page={page}"
        )
        response = requests.get(url)  # Make the HTTP request
        if response.status_code == 200:  # Check if the request was successful
            data = response.json()  # Parse the JSON response
            for doc in data['response']['docs']:
                headline = doc['headline']['main']
                pub_date = doc['pub_date']
                formatted_pub_date = pub_date.replace('T', ' ').split('+')[0]  # Format publication date
                articles.append(f"{headline} | Published on: {formatted_pub_date}")
            if not data['response']['docs']:  # Check if there are no more articles
                break  # Exit the loop
            page += 1  # Move to the next page
        elif response.status_code == 429:  # Check if the rate limit is exceeded
            print("Rate limit exceeded. Waiting before retrying...")
            time.sleep(60)  # Wait for 10 seconds before retrying
        else:  # Handle other errors
            print(f"Error fetching data for {year}-{month}-{day}: {response.status_code}")
            break  # Exit the loop
    return articles  # Return the list of articles

# Define a function to fetch articles for a specified period
def fetch_articles_for_period(start_year, start_month, end_year, end_month, api_key):
    articles = []  # Initialize an empty list to store articles
    start_date = datetime(start_year, start_month, 1)  # Start date of the period
    end_date = datetime(end_year, end_month, get_last_day_of_month(end_year, end_month))  # End date of the period
    current_date = start_date
    while current_date <= end_date:  # Loop until we reach the end date
        articles.extend(fetch_articles_for_date(current_date.year, current_date.month, current_date.day, api_key))
        current_date += timedelta(weeks=1)  # Move to the next week
    return articles  # Return the list of articles

# Function to get the last day of the month
def get_last_day_of_month(year, month):
    return (
        31 if month in [1, 3, 5, 7, 8, 10, 12]
        else 30 if month != 2
        else 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) # leap year
        else 28
    )

api_key = "YourAPIkey"

# Fetch articles for the specific date of 07.10.2023
key_date_articles = fetch_articles_for_date(2023, 10, 7, api_key)

# Fetch articles for the period from September 2023 to January 2024
period_articles = fetch_articles_for_period(2023, 9, 2024, 1, api_key)

combined_articles = key_date_articles + period_articles

# Convert the combined list of articles into a DataFrame
df_articles = pd.DataFrame(combined_articles, columns=['article_info'])

# Split 'article_info' column into three separate columns: 'headline', 'pub_date', and 'pub_time'
split_df = df_articles['article_info'].str.split(r' \| Published on: ', expand=True)

# Split the 'pub_date' column into 'date' and 'time' columns
df_articles[['headline', 'pub_info']] = split_df
df_articles[['pub_date', 'pub_time']] = df_articles['pub_info'].str.split(' ', expand=True)

# Convert 'pub_date' to datetime format for easier manipulation
df_articles['pub_date'] = pd.to_datetime(df_articles['pub_date'])

# Drop the original 'article_info' and 'pub_info' columns as they are no longer needed
df_articles.drop(['article_info', 'pub_info'], axis=1, inplace=True)

# First, sort by publication date
df_articles_sorted = df_articles.sort_values(by='pub_date')

# Then, if 'pub_time' column exists, further sort by publication time
if 'pub_time' in df_articles_sorted:
    df_articles_sorted = df_articles_sorted.sort_values(by=['pub_date', 'pub_time'])

# Save the sorted DataFrame to a CSV file
df_articles_sorted.to_csv('sorted_articles.csv', index=False)

# Load the headlines from the uploaded CSV file
df = pd.read_csv(r'C:\My projects - python\pythonProject5\sorted_articles.csv')

# Convert publication dates to datetime format
df['pub_date'] = pd.to_datetime(df['pub_date'])

# Ensure the dates are within the desired season range starting from 07/10/2023
df = df[(df['pub_date'] >= '2023-10-07') & (df['pub_date'] <= '2024-01-26')]

# Function to get sentiment polarity (as an example of metric calculation)
def get_sentiment(text):
    return TextBlob(text).sentiment.polarity

# Apply the function for sentiment analysis
df['sentiment'] = df['headline'].apply(get_sentiment)

# Load spaCy model for additional text processing if necessary
nlp = spacy.load('en_core_web_sm')

# Function to search for specific phrases indicating support or opposition (modify as needed)
def search_support_opposition(text):
    support_keywords = ['stands with Israel', 'supports Israel', 'in favor of Israel', 'with Israel', 'attack on Israel']
    opposition_keywords = ['against Israel', 'opposes Israel', 'condemns Israel', 'Hamas Attack', 'Genocide', 'accuses Israel']
    for keyword in support_keywords:
        if keyword in text:
            return 1  # Indicates support
    for keyword in opposition_keywords:
        if keyword in text:
            return -1  # Indicates opposition
    return 0  # Neutral or unrelated

# Apply the function to each headline for stance analysis
df['stance'] = df['headline'].apply(search_support_opposition)

# Set 'pub_date' as the DataFrame index and ensure it's a DatetimeIndex for resampling
df.set_index('pub_date', inplace=True)

# Resample by week, ensuring the week starts on the correct day
weekly_sentiment = df.resample('W-SUN')['sentiment'].mean().reset_index()

# Prepare x and y for plotting
x = weekly_sentiment['pub_date'].tolist()
y = weekly_sentiment['sentiment'].tolist()

# Plot
plt.figure(figsize=(15, 8))  # Increase figure size for clarity

# Use plot() directly with x and y
plt.plot(x, y, marker='o', linestyle='-')

# Format the x-axis
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.SUNDAY))

# Automatically format the date labels
plt.gcf().autofmt_xdate()

plt.title('Weekly Average Sentiment')
plt.xlabel('Date (Week Starting From)')
plt.ylabel('Average Sentiment')
plt.grid(True)
plt.tight_layout()

plt.show()

