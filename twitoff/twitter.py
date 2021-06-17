import requests
import spacy
from .models import DB, Tweet, User

#spacy.load('en_core_web_sm')
nlp = spacy.load("../my_model")


def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector


# Add and updates tweets
def add_or_update_user(username):
    try:
        r = requests.get(
            f"https://lambda-ds-twit-assist.herokuapp.com/user/{username}")
        user = r.json()
        user_id = user["twitter_handle"]["id"]

        # This either resepectively grabs or creates a user for our db
        db_user = (User.query.get(user_id)) or User(id=user_id, name=username)
        # This adds the db_user to our database
        DB.session.add(db_user)

        tweets = user["tweets"]

        for tweet in tweets:
            tweet_vector = vectorize_tweet(tweet["full_text"])
            db_tweet = Tweet(id=tweet["id"], text=tweet["full_text"], vect=tweet_vector)
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)

    except Exception as e:
        print("Error processing {}: {}".format(username, e))
        raise e

    else:
        DB.session.commit()


def update_all_users():
    try:
        for user in User.query.all():
            add_or_update_user(user.name)
    except Exception as e:
        print('Error processing {}: {}'.format(user.name, e))
        raise e