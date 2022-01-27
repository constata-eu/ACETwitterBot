import tweepy
import json
import os
import shutil
import time
import subprocess
from tinydb import TinyDB, Query
from access import *


def htmlGenerate(userRepla, textRepla, nameRepla, dateRepla, imageRepla, idRepla):
    template = open('template.html','r')
    tweetHtml = template.read()
    template.close()
    dataReplace = tweetHtml.replace('tweetUser', userRepla).replace('tweetText', textRepla).replace('tweetDate', str(dateRepla)).replace('tweetName', nameRepla).replace('tweetImage', imageRepla).replace('tweetId', str(idRepla))
    outFile = open('{}/{}.html'.format(idRepla,idRepla),'w')
    outFile.write(dataReplace)
    outFile.close()

def htmlGenerateReply(userRepla, textRepla, nameRepla, dateRepla, imageRepla, idRepla, replyUserRepla, replyTextRepla, replyImegeRepla):
    template = open('templateReply.html','r')
    tweetHtml = template.read()
    template.close()
    dataReplace = tweetHtml.replace('tweetUser', userRepla).replace('tweetText', textRepla).replace('tweetDate', str(dateRepla)).replace('tweetName', nameRepla).replace('tweetImage', imageRepla).replace('twNameReply', replyUserRepla).replace('twUserReply', replyUserRepla).replace('twTextReply', replyTextRepla).replace('twImageReply', replyImegeRepla)
    outFile = open('{}/{}.html'.format(idRepla,idRepla),'w')
    outFile.write(dataReplace)
    outFile.close()

def htmlGenerateQuote(userRepla, textRepla, nameRepla, dateRepla, imageRepla, idRepla, quoteNameRepla, quoteUserRepla, quoteTextRepla, quoteImageRepla):
    template = open('templateQuote.html','r')
    tweetHtml = template.read()
    template.close()
    dataReplace = tweetHtml.replace('tweetUser', userRepla).replace('tweetText', textRepla).replace('tweetDate', str(dateRepla)).replace('tweetName', nameRepla).replace('tweetImage', imageRepla).replace('twNameQuote', quoteUserRepla).replace('twTextQuote', quoteTextRepla).replace('twImageQuote', quoteImageRepla).replace('twUserQuote', quoteUserRepla)
    outFile = open('{}/{}.html'.format(idRepla,idRepla),'w')
    outFile.write(dataReplace)
    outFile.close()

db = TinyDB('db.json')
stampDocuments = Query()


while True:
    try:

        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth)


        lastTweetFile = open('lastTweetNumber','r')
        lastTweetID = lastTweetFile.read()
        lastTweetFile = open('lastTweetNumber','r')
        lastTweetStamp = lastTweetFile.read()
        hashtags = tweepy.Cursor(api.search_tweets, q=TEXT_TO_SEARCH, since_id=lastTweetID)


        for tweets in reversed(list(hashtags.items())):
            if tweets.text.startswith('RT'):
                continue
            if tweets.text.startswith('@constataEu 📥 ¡Tu tweet fue sellado!'):
                continue
            os.mkdir('{}'.format(tweets.id))
            print(time.strftime("%c"),"| Se enviará a sellar el tweet", tweets.id, tweets.created_at)
            print('Cuando se publique el boletín, responderé directamente al tweet de  @{} con el certificado.'.format(tweets.user.screen_name), tweets.id)
            #api.update_status('@{} Estoy trabajando para sellar el tweet. En breve, responderé este tweet con el certificado.'.format(tweets.user.screen_name), in_reply_to_status_id=tweets.id)
            with open('{}/{}.json'.format(tweets.id,tweets.id), 'w') as file:
                json.dump(tweets._json, file, indent=2)
            if tweets.in_reply_to_status_id:
                print('El tweet' ,tweets.id, 'es reply',tweets.in_reply_to_status_id)
                replyID = api.get_status(id=tweets.in_reply_to_status_id)
                htmlGenerateReply(tweets.user.name,tweets.text,tweets.user.screen_name,tweets.created_at,tweets.user.profile_image_url_https,tweets.id,tweets.in_reply_to_screen_name,replyID.text,replyID.user.profile_image_url_https)
            elif tweets.is_quote_status:
                print('El tweet' ,tweets.id, 'es quote',tweets.is_quote_status)
                htmlGenerateQuote(tweets.user.name,tweets.text,tweets.user.screen_name,tweets.created_at,tweets.user.profile_image_url_https,tweets.id,tweets.quoted_status.user.screen_name,tweets.quoted_status.user.name,tweets.quoted_status.text,tweets.quoted_status.user.profile_image_url_https)
            else:
                print('El tweet' ,tweets.id, 'es tweet',tweets.in_reply_to_status_id)
                htmlGenerate(tweets.user.name,tweets.text,tweets.user.screen_name,tweets.created_at,tweets.user.profile_image_url,tweets.id)
            zipPath = '{}.zip'.format(tweets.id)
            archivo_zip = shutil.make_archive(str(tweets.id), "zip", str(tweets.id))
            shutil.rmtree(str(tweets.id))

            outputStamp = subprocess.Popen(["./constata-cli-linux", "--password", "{}".format(CONSTATA_PASS), "stamp", "{}".format(zipPath)], stdout=subprocess.PIPE, universal_newlines=True)
            outputStamp.wait()
            print("----------------------------------------------------------------------------------------------------")
            stampOut = outputStamp.stdout.read()
            stampOutJson = json.loads(stampOut)
            bulletin_id = stampOutJson['bulletin_id']
            state = stampOutJson['bulletins']['{}'.format(bulletin_id)]['state']
            document_id = stampOutJson['parts'][0]['document_id']

            db.insert({'bulletin_id': bulletin_id, 'document_id': document_id, 'tw_id': tweets.id, 'state': state, 'userToReply': tweets.user.screen_name})
            lastTweetStamp = tweets.id

            os.remove('{}'.format(zipPath))

        if lastTweetID != lastTweetStamp:
            lastTweet = lastTweetStamp
            lastTweetFile = open('lastTweetNumber','w')
            lastTweetFile.write(str(lastTweet))

        lastTweetFile.close()

        print("Último tweet: ",lastTweetID)
        print('Esperando 60 segundos')
        time.sleep(60)#Serán 60'

        searchDraft = db.search(stampDocuments.state == 'Draft')
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
            itemState = showJson['bulletins']['{}'.format(bullId)]['state']
            if itemState == 'Published':
                print("Ya está publicado :) ", docId)
                outputHtml = open("{}.html".format(tweetId), "w")
                outputFetchProof = subprocess.Popen(["./constata-cli-linux", "--password", "{}".format(CONSTATA_PASS), "fetch-proof", "{}".format(docId)], stdout=outputHtml, universal_newlines=True)
                outputFetchProof.wait()
                db.update({'state': 'FetchProofed'}, stampDocuments.document_id == '{}'.format(docId))
                print("html almacenado y cambiado state del documento a FetchProofed")
                uploadHtml = subprocess.Popen(["s3cmd", "--add-header=content-disposition:attachment", "put", "-P", "{}.html".format(tweetId), "s3://aceconstata/{}/{}.html".format(SPACES_FOLDER, tweetId)], stdout=subprocess.PIPE, universal_newlines=True)
                uploadHtml.wait()
                print("html enviado a Digital Ocean Spaces")
                os.remove('{}.html'.format(tweetId))
                print("html eliminado de storage local")
                api.update_status('@{} 📥 ¡Tu tweet fue sellado! Descarga el certificado-> https://aceconstata.ams3.digitaloceanspaces.com/{}/{}.html'.format(user2Reply, SPACES_FOLDER, tweetId), in_reply_to_status_id=tweetId)
                print("¡Tu tweet fue sellado! Descarga el certificado-> https://aceconstata.ams3.digitaloceanspaces.com/{}/{}.html".format(SPACES_FOLDER, tweetId))

    except IndexError:
        print('No hay un último tweet en el rango definido')
        print('Esperando 60 segundos para reintentar')
        time.sleep(60)
