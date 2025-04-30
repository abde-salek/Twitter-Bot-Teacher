from tweet_poster import tweet_poster

# Test Case 1: tweet_poster()
print("Test Case 1: tweet_poster()")
tweet_id = tweet_poster()
print(f"Tweet ID: {tweet_id}")
if tweet_id:
    print("Tweet posted successfully")
else:
    print("Tweet posting failed")