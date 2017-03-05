# StockTalk3
Data collection toolkit (https://github.com/anfederico/Stocktalk) for social media analytics ported to Python 3.

## Code Examples

#### Mining Twitter

```python
from stocktalk import TwitterAxe

#credentials
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN = ""
ACCESS_SECRET = ""

axe = TwitterAxe(api=twitter.Api(consumer_key=CONSUMER_KEY,
                  consumer_secret=CONSUMER_SECRET,
                  access_token_key=ACCESS_TOKEN,
                  access_token_secret=ACCESS_SECRET))

#mining settings
minePeriod        = 60*5     # Mine Twitter for 5 minutes
requestFrequency  = 30*1     # Request tweets every 30 seconds
analyzeFrequency  = 60*1     # Analyze tweets every 1 minute
requestAmount     = 100      # With each request pull 100 tweets (max = 100)
similarityCutoff  = 90       # Filter out tweets with 90% similarity (default = 90)

# start mining
axe.mine("Apple", minePeriod, requestFrequency, analyzeFrequency, requestAmount, similarityCutoff)
```

```text
Mine complete from
[2016/10/14 02:37:16 PM] - [2016/10/14 02:42:26 PM]
```
#### Save & Explore Data

```python
axe.showInventory()
axe.showUniqueTweets()
axe.showFilteredTweets()
axe.showTimeSeries()

axe.exportUniqueTweets()
axe.exportFilteredTweets()
```

```text
Inventory
Unique Tweets: 398
Filtered Tweets: 73

Unique Tweets
              DATE_TIME                                               TEXT
0   2017-03-05 09:49:19  @BenPhillipsUK you should pee into a bottle an...
1   2017-03-05 09:49:18  RT @SonyMusicGlobal: #ZAYNmoji is here. https:...
2   2017-03-05 09:49:18  RT @LittleMix: #NoMoreSadSongs feat @machinegu...
... ...
395 2017-03-05 09:53:12  @Apple @AppleSupport than ‘oh, sorry, just wai...
396 2017-03-05 09:53:11  Carol Dysart reveals how to understand ideal c...
397 2017-03-05 09:53:10  R Shawn McBride reveals expert business tips &...
[398 rows x 2 columns]

Filtered Tweets
             DATE_TIME                                               TEXT
0  2017-03-05 09:49:10  RT @MayWardFlyersPH: Titig ng Pag-ibig Single ...
1  2017-03-05 09:49:05  RT @MayWardFlyersPH: Titig ng Pag-ibig Single ...
2  2017-03-05 09:48:58  Lazy Sunday morning with some #comfortfood 🍎🌸a...
... ...
70 2017-03-05 09:51:33  RT @uperdeepes: Now on #Itunes go support @iam...
71 2017-03-05 09:53:28  RT @MayWardFlyersPH: Titig ng Pag-ibig Single ...
72 2017-03-05 09:53:17  RT @MayWardFlyersPH: Titig ng Pag-ibig Single ...
[73 rows x 2 columns]

Time Series
                  TIME  SENTIMENT  TWEETS
0  2017-03-05 11:50:06      0.354      67
1  2017-03-05 11:51:06      0.202      74
2  2017-03-05 11:52:07      0.279      85
3  2017-03-05 11:53:24      0.342     149
```

#### Visualize Sentiment Analysis

```python
axe.showPlot()
axe.savePlot(name='apple' [, width = 6, height = 4.5])
```
<!-- <img src="https://github.com/xenu256/StockTalk3/blob/master/outputs/apple.png"  width=60%> -->

## Underlying Features

#### Spam Filtering
```python
from stocktalk import similarityScore

stringOne = "Lawsuits are piling up against Tesla Motors (TSLA) over the Solar City (SCTY) merger"
stringTwo = "Lawsuits piling up against Tesla Motors (TSLA) with the Solar City (SCTY) merger"
print(similarityScore(s1=stringOne, s2=stringTwo))
# 95.12%

stringTwo   = "Lawsuits piling up against Tesla Motors (TSLA) with the Solar City (SCTY) merger"
stringThree = "Bad news for Tesla Motors (TSLA) over the Solar City (SCTY) merger"
print(similarityScore(s1=stringTwo, s2=stringThree))
# 82.19%

stringThree = "Bad news for Tesla Motors (TSLA) over the Solar City (SCTY) merger"
stringFour  = "Tesla Motors (TSLA) will not need to raise equity or debt before the end of the year"
print similarityScore(stringThree, stringFour)
# 59.33%
```

#### Text Processing
```python
from stocktalk import filter_tweets

textOne = "@TeslaMotors shares jump as shipments more than double! #winning"
print(filter_tweets(text=textOne))
# shares jump as shipments more than double winning

textTwo = "Tesla announces its best sales quarter: http://trib.al/RbTxvSu $TSLA" 
print(filter_tweets(text=textTwo))
# tesla announces its best sales quarter

textThree = "Tesla $TSLA reports deliveries of 24500, above most views."
print(filter_tweets(text=textThree))
# tesla reports deliveries of number above most views
```

#### Sentiment Analysis
```python
from stocktalk import sentimentScore

textOne = "shares jump as shipments more than double winning"
print(sentimentScore(texts=[textOne]))
# 0.706

textTwo = "tesla reports deliveries of number above most views"
print(sentimentScore(texts=[textTwo]))
# 0.077

textThree = "not looking good for tesla competition on the rise"
print(sentimentScore(texts=[textThree]))
# -0.341
```

