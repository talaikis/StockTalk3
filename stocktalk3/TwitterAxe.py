from datetime import datetime
from csv import DictWriter
from re import sub
from time import (time, localtime, strftime)
from os.path import (join, dirname)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from pandas import DataFrame
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import schedule


BASE_PATH = dirname(__file__)

def twitter_date(value):
    split_date = value.split()
    del split_date[0], split_date[-2]
    value = ' '.join(split_date) # format: Fri Nov 07 17:57:59 +0000 2016
    return datetime.strptime(value, '%b %d %H:%M:%S %Y')


def filter_tweets(text):
    try:
        text = text.lower()
        text = sub(r"[0-9]+", "number", text)
        text = sub(r"#", "", text)
        text = sub(r"\n", "", text)
        text = text.replace('$', '@')
        text = sub(r"@[^\s]+", "", text)
        text = sub(r"(http|https)://[^\s]*", "", text)
        text = sub(r"[^\s]+@[^\s]+", "", text)
        text = sub(r'[^a-z A-Z]+', '', text)
    except Exception as e:
        print(e)

    return text


def similarityScore(s1, s2):
    try:
        if len(s1) == 0: return len(s2)
        elif len(s2) == 0: return len(s1)
        v0 = [None]*(len(s2) + 1)
        v1 = [None]*(len(s2) + 1)
        for i in range(len(v0)):
            v0[i] = i
        for i in range(len(s1)):
            v1[0] = i + 1
            for j in range(len(s2)):
                cost = 0 if s1[i] == s2[j] else 1
                v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
            for j in range(len(v0)):
                v0[j] = v1[j]
    except Exception as e:
        print(e)

    return 100-((float(v1[len(s2)])/(len(s1)+len(s2)))*100)


def sentimentScore(texts):
    scores = []
    for text in texts:
        score = SentimentIntensityAnalyzer().polarity_scores(text)["compound"]
        if score != 0: scores.append(score)
    try:
        return round(sum(scores)/len(scores), 3)
    except Exception as e:
        print(e)
        return 0


class TwitterAxe:

    def __init__(self, api):
        self.api = api
        self.query            = ""
        self.amount           = 50
        self.cutoff           = 90
        self.filteredOutCount = 0
        self.filteredInCount  = 0
        self.filteredIn       = []
        self.filteredOut      = []
        self.binnedTweets     = []
        self.groupedTweets    = []
        self.timeSeries       = []

    def requestTweets(self):
        try:
            tweets = self.api.GetSearch(term=self.query, count=self.amount, \
                lang='en', result_type="recent", include_entities=False)
        except Exception as e:
            print(e)

        for tweet in tweets:
            try:
                tweet_text = tweet.text
                tweet_time = tweet.created_at

                t1 = filter_tweets(text=tweet_text)

                highScore = 0
                for t2 in self.binnedTweets:
                    score = similarityScore(t1, t2)
                    if score > highScore: highScore = score

                if highScore < self.cutoff:
                    self.filteredInCount += 1
                    if len(self.binnedTweets) >= 50:
                        self.binnedTweets.pop()
                    self.binnedTweets.insert(0, t1)
                    self.groupedTweets.append(t1)
                    self.filteredIn.append({'DATE_TIME': twitter_date(value=tweet_time), 'TEXT': tweet_text })
                else:
                    self.filteredOutCount += 1
                    self.filteredOut.append({'DATE_TIME': twitter_date(value=tweet_time), 'TEXT': tweet_text })
            except Exception as e:
                print(e)

    def analyzeGroup(self):
        try:
            self.timeSeries.append({ "TIME"      : strftime("%Y-%m-%d %H:%M:%S", localtime()),
                                     "SENTIMENT" : sentimentScore(texts=self.groupedTweets),
                                     "TWEETS"    : len(self.groupedTweets)})
            self.groupedTweets = []
        except Exception as e:
            print(e)

    def mine(self, query, minePeriod, requestFrequency, analyzeFrequency, requestAmount = 50, similarityCutoff = 90):
        try:
            self.query = query
            self.cutoff = similarityCutoff
            self.amount = requestAmount

            startStr = strftime("[%Y-%m-%d %H:%M:%S]", localtime())
            schedule.every(requestFrequency).seconds.do(self.requestTweets)
            schedule.every(analyzeFrequency).seconds.do(self.analyzeGroup)

            end = time()+minePeriod
            while time() <= end:
                schedule.run_pending()

            endStr = strftime("[%Y-%m-%d %H:%M:%S]", localtime())
            print("Mine complete from\n" + startStr +" - " + endStr +"\n")
        except Exception as e:
            print(e)

    def showInventory(self):
        print("\033[1m"+"Inventory"+"\033[0m")
        print("Unique Tweets: "+str(self.filteredInCount))
        print("Filtered Tweets: "+str(self.filteredOutCount))
        print()

    def showUniqueTweets(self):
        print("\033[1m"+"Unique Tweets"+"\033[0m")
        print(DataFrame(self.filteredIn))

    def exportUniqueTweets(self):
        file_name = join(BASE_PATH, "outputs", "unique_tweets.csv")
        outfile = open(file_name, 'w')
        for tweet in self.filteredIn:
            try: outfile.write('"' + tweet['DATE_TIME'].strftime('%Y-%m-%d %H:%M:%S') + '"; "' + tweet['TEXT'] + '"\n')
            except Exception as e: print(e)
        outfile.close()
        print("Exported unique tweets to {}".format(file_name))

    def showFilteredTweets(self):
        print("\033[1m"+"Filtered Tweets"+"\033[0m")
        print(DataFrame(self.filteredOut))
        print()

    def exportFilteredTweets(self):
        file_name = join(BASE_PATH, "outputs", "filtered_tweets.csv")
        outfile = open(file_name, 'w')
        for tweet in self.filteredOut:
            try: outfile.write('"' + tweet['DATE_TIME'].strftime('%Y-%m-%d %H:%M:%S') + '"; "'+ tweet['TEXT']+'"\n')
            except Exception as e: print(e)
        outfile.close()
        print("Exported filtered tweets to {}".format(file_name))

    def showTimeSeries(self):
        print("\033[1m"+"Time Series"+"\033[0m")
        columns = ["TIME", "SENTIMENT", "TWEETS"]
        print(DataFrame(self.timeSeries, columns=columns))
        print()

    def exportTimeSeries(self):
        file_name = join(BASE_PATH, "outputs", "sentiment.csv")
        with open(file_name, 'w') as outfile:
            writer = DictWriter(outfile, fieldnames=['TIME', 'SENTIMENT', 'TWEETS'])
            writer.writeheader()
            for datapoint in self.timeSeries:
                writer.writerow({ "TIME"      : datapoint["TIME"],
                                  "SENTIMENT" : datapoint["SENTIMENT"],
                                  "TWEETS"    : datapoint["TWEETS"]})
        print("Exported time series data to {}".format(file_name))

    def savePlot(self, name, width=6, height=4.5):
        timestamps = []
        sentiment = []
        tweets = []
        for data_point in self.timeSeries:
            timestamps.append(datetime.strptime(data_point["TIME"], '%Y-%m-%d %H:%M:%S'))
            sentiment.append(data_point["SENTIMENT"])
            tweets.append(data_point["TWEETS"])

        # Plot setup
        ax1 = plt.figure(figsize=(width, height)).add_subplot(111)
        ax1.spines["top"].set_visible(False)
        ax1.get_xaxis().tick_bottom()
        ax1.get_yaxis().tick_left()
        ax1.xaxis.set_major_formatter(DateFormatter('%m-%d %H:%M'))
        lns1 = ax1.plot(timestamps, sentiment, color="dimgrey", lw=0.75, label="Sentiment")
        plt.yticks(fontsize=8)
        plt.ylim(ymin=-1, ymax=1)
        plt.xticks(rotation=50, fontsize=8)
        ax2 = ax1.twinx()
        lns2 = ax2.plot(timestamps, tweets, color="dodgerblue", lw=0.5, label="Tweets")
        ax2.margins(0.05)
        plt.yticks(fontsize=8)

        # Labeling
        ax1.legend(lns1+lns2, ['Sentiment', 'Tweets'], loc=0, frameon=False, fontsize=6)
        ax1.set_ylabel("Sentiment", weight="light", rotation=90, fontsize=9, labelpad=1)
        ax2.set_ylabel("Tweets", weight="light", rotation=-90, fontsize=9, labelpad=15)
        plt.title("Tweet Sentiment", weight ="light", fontsize=12, y=1.08)
        plt.ylim(ymin=0)
        plt.tight_layout()
        file_name = join(BASE_PATH, "outputs", name+".png")
        plt.savefig(file_name)
        print("Saved plot {}".format(file_name))

    def showPlot(self):
        timestamps = []
        sentiment = []
        tweets = []
        for data_point in self.timeSeries:
            timestamps.append(datetime.strptime(data_point["TIME"], '%Y-%m-%d %H:%M:%S'))
            sentiment.append(data_point["SENTIMENT"])
            tweets.append(data_point["TWEETS"])

        # Plot setup
        ax1 = plt.figure(figsize=(6, 4.5)).add_subplot(111)
        ax1.spines["top"].set_visible(False)
        ax1.get_xaxis().tick_bottom()
        ax1.get_yaxis().tick_left()
        ax1.xaxis.set_major_formatter(DateFormatter('%m-%d %H:%M'))
        lns1 = ax1.plot(timestamps, sentiment, color="dimgrey", lw=0.75, label="Sentiment")
        plt.yticks(fontsize=8)
        plt.ylim(ymin=-1, ymax=1)
        plt.xticks(rotation=50, fontsize=8)
        ax2 = ax1.twinx()
        lns2 = ax2.plot(timestamps, tweets, color="dodgerblue", lw=0.5, label="Tweets")
        ax2.margins(0.05)
        plt.yticks(fontsize=8)

        # Labeling
        ax1.legend(lns1+lns2, ['Sentiment', 'Tweets'], loc=0, frameon=False, fontsize=6)
        ax1.set_ylabel("Sentiment", weight="light", rotation=90, fontsize=9, labelpad=1)
        ax2.set_ylabel("Tweets", weight="light", rotation=-90, fontsize=9, labelpad=15)
        plt.title("Tweet Sentiment", weight ="light", fontsize=12, y=1.08)
        plt.ylim(ymin=0)
        plt.tight_layout()
        plt.show()
