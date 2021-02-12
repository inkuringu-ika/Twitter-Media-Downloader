import requests
import json
import time
from tqdm import tqdm
import urllib
import sys
import os

input_url = input("Tweet URL: ")
input_url_parsed = urllib.parse.urlparse(input_url)
if(input_url_parsed.netloc == "twitter.com"):
    user_id = input_url_parsed.path.split("/")[1]
    tweet_id = input_url_parsed.path.split("/")[3]
    print("user_id: " + user_id)
    print("tweet_id: " + tweet_id)
else:
    sys.exit(1)

Authorization = 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'
guest_token_age = 10800
guest_token_expires = int(time.time()) + guest_token_age

headers = {
    'Authorization': Authorization
}
result = requests.post("https://api.twitter.com/1.1/guest/activate.json", headers=headers)
guest_token = json.loads(result.text)["guest_token"]

headers = {
    'Authorization': Authorization,
    'x-guest-token': guest_token
}
result = requests.get("https://api.twitter.com/1.1/statuses/show/" + tweet_id + ".json?cards_platform=Web-12&include_cards=1&include_reply_count=1&include_user_entities=0&tweet_mode=extended", headers=headers)
result_json = json.loads(result.text)
for media_index, media in enumerate(result_json["extended_entities"]["media"]):
    media_type = media["type"]
    if(media_type == "video" or media_type == "animated_gif"):
        variants_bitrate = []
        for variant in media["video_info"]["variants"]:
            if(variant["content_type"] == "video/mp4"):
                variants_bitrate.append(variant["bitrate"])
            else:
                variants_bitrate.append(-1)
        media_url = media["video_info"]["variants"][variants_bitrate.index(max(variants_bitrate))]["url"]
        print(media_url)
        r = requests.get(media_url, stream=True, timeout=10)
        r.raise_for_status()
        pbar = tqdm(total=int(r.headers["content-length"]), unit="B", unit_scale=True)
        with open(tweet_id + "_video_" + str(media_index) + "." + urllib.parse.urlparse(media_url).path.split(".")[-1], 'wb') as file:
            for chunk in r.iter_content(chunk_size=1024):
                file.write(chunk)
                pbar.update(len(chunk))
            pbar.close()
            file.close()
    elif(media_type == "photo"):
        media_url = media["media_url_https"] + "?name=orig"
        print(media_url)
        r = requests.get(media_url, stream=True, timeout=10)
        r.raise_for_status()
        pbar = tqdm(total=int(r.headers["content-length"]), unit="B", unit_scale=True)
        with open(tweet_id + "_photo_" + str(media_index) + "." + urllib.parse.urlparse(media_url).path.split(".")[-1], 'wb') as file:
            for chunk in r.iter_content(chunk_size=1024):
                file.write(chunk)
                pbar.update(len(chunk))
            pbar.close()
            file.close()
    else:
        print('Unsupported type "' + media_type + '"')
