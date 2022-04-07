#!/usr/bin/env python3

import tweepy
import json
import os
import shutil
import time
import subprocess
import requests
from tinydb import TinyDB, Query
from access import *

def send_tl_message(mge_error):
    bot_token = TL_TOKEN
    URL = "https://api.telegram.org/bot" + bot_token + "/sendMessage"
    headers = {
        'Content-Type': 'application/json',
    }
    chat_id = CHAT_ID
    text = "ACE Twitter bot ALERT!" + " (" + ENVIRONMENT + ")" + "\n" + mge_error
    data = '{"chat_id": "' + chat_id + '", "text": "' + text + '", "disable_notification": false"'+ '"}'

    try:
        requests.post(URL, headers=headers, data=data)
        return 'Mensaje enviado a Telegram'

    except Exception as e:
        print( 'La Exception >> ' + type(e).__name__ )
        return 'Error interno al enviar el mensaje a Telegram'


def html_generate(userRepla, textRepla, nameRepla, dateRepla, imageRepla, idRepla, urlImageRepla):
    template = open('template.html','r')
    tweetHtml = template.read()
    template.close()
    dataReplace = tweetHtml.replace('tweetUser', userRepla).replace('tweetText', textRepla).replace('tweetDate', str(dateRepla)).replace('tweetName', nameRepla).replace('tweetImage', imageRepla).replace('tweetId', str(idRepla)).replace('media_url_https_code_or_nothing', urlImageRepla)
    outFile = open('{}/{}.html'.format(idRepla,idRepla),'w')
    outFile.write(dataReplace)
    outFile.close()

def html_generate_reply(userRepla, textRepla, nameRepla, dateRepla, imageRepla, idRepla, replyUserRepla, replyTextRepla, replyImageRepla, replyNameRepla, urlImageRepla):
    template = open('templateReply.html','r')
    tweetHtml = template.read()
    template.close()
    dataReplace = tweetHtml.replace('tweetUser', userRepla).replace('tweetText', textRepla).replace('tweetDate', str(dateRepla)).replace('tweetName', nameRepla).replace('tweetImage', imageRepla).replace('twNameReply', replyUserRepla).replace('twUserReply', replyNameRepla).replace('twTextReply', replyTextRepla).replace('twImageReply', replyImageRepla).replace('tweetId', str(idRepla)).replace('image_url_reply',urlImageRepla)
    outFile = open('{}/{}.html'.format(idRepla,idRepla),'w')
    outFile.write(dataReplace)
    outFile.close()

def html_generate_quote(userRepla, textRepla, nameRepla, dateRepla, imageRepla, idRepla, quoteNameRepla, quoteUserRepla, quoteTextRepla, quoteImageRepla, quoteUrlImgRepla):
    template = open('templateQuote.html','r')
    tweetHtml = template.read()
    template.close()
    dataReplace = tweetHtml.replace('tweetUser', userRepla).replace('tweetText', textRepla).replace('tweetDate', str(dateRepla)).replace('tweetName', nameRepla).replace('tweetImage', imageRepla).replace('twNamQuote', quoteNameRepla).replace('twTextQuote', quoteTextRepla).replace('twImageQuote', quoteImageRepla).replace('twUserQuote', quoteUserRepla).replace('tweetId', str(idRepla)).replace('image_url_quote', quoteUrlImgRepla)
    outFile = open('{}/{}.html'.format(idRepla,idRepla),'w')
    outFile.write(dataReplace)
    outFile.close()

def is_reply_to_constata(tweets):
    mentions_total = len(tweets.entities["user_mentions"])
    for mentions in range(0,mentions_total):
        user_screen_name_mentions = tweets.entities["user_mentions"][mentions]["screen_name"]
        if user_screen_name_mentions == "constataEu":
            #Si menciona a constata
            return False
    else:
        #Si no menciona a constata
        return True

def tweet_stamper(tweets):
    print(time.strftime("%c"),"| Se enviará a sellar el tweet", tweets.id, tweets.created_at)
    print('Cuando se publique el boletín, responderé directamente al tweet de  @{} con el certificado.'.format(tweets.user.screen_name), tweets.id)
    #api.update_status('@{} Estoy trabajando para sellar el tweet. En breve, responderé este tweet con el certificado.'.format(tweets.user.screen_name), in_reply_to_status_id=tweets.id)
    with open('{}/{}.json'.format(tweets.id,tweets.id), 'w') as file:
        json.dump(tweets._json, file, indent=2)
    zipPath = '{}.zip'.format(tweets.id)
    archivo_zip = shutil.make_archive(str(tweets.id), "zip", str(tweets.id))
    shutil.rmtree(str(tweets.id))

    outputStamp = subprocess.Popen(["./constata-cli-linux", "--password", "{}".format(CONSTATA_PASS), "stamp", "{}".format(zipPath)], stdout=subprocess.PIPE, universal_newlines=True)
    outputStamp.wait()
    print("--------------------------------------------------------------------------------")
    stampOut = outputStamp.stdout.read()
    stampOutJson = json.loads(stampOut)
    bulletin_id = stampOutJson['bulletin_id']
    state = (stampOutJson['bulletins']['{}'.format(bulletin_id)]['state']).lower()
    document_id = stampOutJson['parts'][0]['document_id']

    db.insert({'bulletin_id': bulletin_id, 'document_id': document_id, 'tw_id': tweets.id, 'state': state, 'userToReply': tweets.user.screen_name})
    lastTweetStamp = tweets.id

    os.remove('{}'.format(zipPath))
    #Da like al tweet
    tweets.favorite()


db = TinyDB('db.json')
stampDocuments = Query()
counter = 0

while True:
    try:

        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth)


        lastTweetFile = open('lastTweetNumber','r')
        lastTweetID = lastTweetFile.read()
        lastTweetFile = open('lastTweetNumber','r')
        lastTweetStamp = lastTweetFile.read()
        hashtags = tweepy.Cursor(api.search_tweets, q=TEXT_TO_SEARCH, since_id=lastTweetID, tweet_mode="extended")


        for tweets in reversed(list(hashtags.items())):
            if tweets.full_text.startswith('RT'):
                continue
            if tweets.full_text.startswith('@constataEu 📥 ¡Tu tweet fue sellado!'):
                continue
            #os.mkdir('{}'.format(tweets.id))
            #print(time.strftime("%c"),"| Se enviará a sellar el tweet", tweets.id, tweets.created_at)
            #print('Cuando se publique el boletín, responderé directamente al tweet de  @{} con el certificado.'.format(tweets.user.screen_name), tweets.id)
            ##api.update_status('@{} Estoy trabajando para sellar el tweet. En breve, responderé este tweet con el certificado.'.format(tweets.user.screen_name), in_reply_to_status_id=tweets.id)
            #with open('{}/{}.json'.format(tweets.id,tweets.id), 'w') as file:
            #    json.dump(tweets._json, file, indent=2)
            if tweets.in_reply_to_status_id and is_reply_to_constata(tweets):
                print('El tweet' ,tweets.id, 'es reply',tweets.in_reply_to_status_id)
                replyID = api.get_status(id=tweets.in_reply_to_status_id, tweet_mode="extended")
                if 'media' in replyID.entities:
                    image_url_reply = replyID.entities["media"][0]["media_url_https"]
                    tweet_image_reply = '<div class="Media" style= "border-left:2px solid #dddddd;margin-left:23px;"> <img style= "border-radius: 10px;width: 90%; margin: 2px; margin-left:36px;" src="' + image_url_reply + '" alt="media url failed :("> </div>'
                else:
                    tweet_image_reply = ""
                os.mkdir('{}'.format(tweets.id))
                html_generate_reply(tweets.user.name,tweets.full_text,tweets.user.screen_name,tweets.created_at,tweets.user.profile_image_url_https,tweets.id,tweets.in_reply_to_screen_name,replyID.full_text,replyID.user.profile_image_url_https,replyID.user.name,tweet_image_reply)
                tweet_stamper(tweets)
            elif tweets.is_quote_status:
                print('El tweet' ,tweets.id, 'es quote',tweets.is_quote_status)
                if 'media' in tweets.quoted_status.entities:
                    image_url = tweets.quoted_status.entities["media"][0]["media_url_https"]
                    tweet_image_quote = '<div class="Media"> <img style= "border-radius:10px; width:100%; margin:2px;" src="' + image_url + '" alt="media url failed :("> </div>'
                else:
                    tweet_image_quote = ""
                os.mkdir('{}'.format(tweets.id))
                html_generate_quote(tweets.user.name,tweets.full_text,tweets.user.screen_name,tweets.created_at,tweets.user.profile_image_url_https,tweets.id,tweets.quoted_status.user.screen_name,tweets.quoted_status.user.name,tweets.quoted_status.full_text,tweets.quoted_status.user.profile_image_url_https, tweet_image_quote)
                tweet_stamper(tweets)
            else:
                print('El tweet' ,tweets.id, 'es tweet',tweets.in_reply_to_status_id)
                if 'media' in tweets.entities:
                    image_url = tweets.entities["media"][0]["media_url_https"]
                    tweet_image = '<div class="Media"> <img style= "border-radius: 10px;width: 100%; margin: 2px;" src="' + image_url + '" alt="media url failed :("> </div>'
                else:
                    tweet_image = ""
                os.mkdir('{}'.format(tweets.id))
                html_generate(tweets.user.name,tweets.full_text,tweets.user.screen_name,tweets.created_at,tweets.user.profile_image_url,tweets.id, tweet_image)
                tweet_stamper(tweets)
            #zipPath = '{}.zip'.format(tweets.id)
            #archivo_zip = shutil.make_archive(str(tweets.id), "zip", str(tweets.id))
            #shutil.rmtree(str(tweets.id))

            #outputStamp = subprocess.Popen(["./constata-cli-linux", "--password", "{}".format(CONSTATA_PASS), "stamp", "{}".format(zipPath)], stdout=subprocess.PIPE, universal_newlines=True)
            #outputStamp.wait()
            #print("--------------------------------------------------------------------------------")
            #stampOut = outputStamp.stdout.read()
            #stampOutJson = json.loads(stampOut)
            #bulletin_id = stampOutJson['bulletin_id']
            #state = (stampOutJson['bulletins']['{}'.format(bulletin_id)]['state']).lower()
            #document_id = stampOutJson['parts'][0]['document_id']

            #db.insert({'bulletin_id': bulletin_id, 'document_id': document_id, 'tw_id': tweets.id, 'state': state, 'userToReply': tweets.user.screen_name})
            #lastTweetStamp = tweets.id

            #os.remove('{}'.format(zipPath))
            ##Da like al tweet
            #tweets.favorite()

        if lastTweetID != lastTweetStamp:
            lastTweet = lastTweetStamp
            lastTweetFile = open('lastTweetNumber','w')
            lastTweetFile.write(str(lastTweet))

        lastTweetFile.close()

        print("Último tweet: ",lastTweetID)
        print('Esperando 60 segundos')
        time.sleep(60)#Serán 60'

        searchDraft = db.search(stampDocuments.state == 'draft')
        for item in searchDraft:
            docId = item['document_id']
            tweetId = item['tw_id']
            user2Reply = item['userToReply']

            print("En draft (esperando publicación en Blockchain)",docId)

            outputShow = subprocess.Popen(["./constata-cli-linux", "--password", "{}".format(CONSTATA_PASS), "show", "{}".format(docId)], stdout=subprocess.PIPE, universal_newlines=True)
            outputShow.wait()
            showOut = outputShow.stdout.read()
            showJson = json.loads(showOut)
            bullId = showJson['bulletin_id']
            itemState = (showJson['bulletins']['{}'.format(bullId)]['state']).lower()
            if itemState == 'published':
                print("Ya está publicado :) ", docId)
                outputHtml = open("{}.html".format(tweetId), "w")
                outputFetchProof = subprocess.Popen(["./constata-cli-linux", "--password", "{}".format(CONSTATA_PASS), "fetch-proof", "{}".format(docId)], stdout=outputHtml, universal_newlines=True)
                outputFetchProof.wait()
                db.update({'state': 'FetchProofed'}, stampDocuments.document_id == '{}'.format(docId))
                print("html almacenado y cambiado state del documento a FetchProofed")
                uploadHtml = subprocess.Popen(["s3cmd", "--add-header=content-disposition:attachment", "put", "-P", "{}.html".format(tweetId), "s3://aceconstata/{}/{}.html".format(ENVIRONMENT, tweetId)], stdout=subprocess.PIPE, universal_newlines=True)
                uploadHtml.wait()
                print("html enviado a Digital Ocean Spaces")
                os.remove('{}.html'.format(tweetId))
                print("html eliminado de storage local")
                api.update_status('@{} 📥 ¡Tu tweet fue sellado! Descarga el certificado-> https://aceconstata.ams3.digitaloceanspaces.com/{}/{}.html'.format(user2Reply, ENVIRONMENT, tweetId), in_reply_to_status_id=tweetId)
                print("¡Tu tweet fue sellado! Descarga el certificado-> https://aceconstata.ams3.digitaloceanspaces.com/{}/{}.html".format(ENVIRONMENT, tweetId))

    except Exception as e:
        print(repr(e))
        counter += 1
        if counter > 4:
            mge_error = 'The last error of 5 is:\n'+ repr(e)
            print(send_tl_message(mge_error))
            counter = 0
        print('Esperando 60 segundos para reintentar')
        time.sleep(60)
