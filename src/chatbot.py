# importing Telegram API
import nltk
import numpy as np
import string
from telegram.ext import Updater
from telegram.ext import CommandHandler

from nltk.tag.stanford import StanfordNERTagger
from bert_serving.client import BertClient
import csv

text1 = '''
All happy families are alike; each unhappy family is unhappy in its own way. All was confusion in the Oblonskys’ house.  The wife had found out that the husband was having an affair with their former French governess, and had announced to the husband that she could not live in the same house with him.  This situation had continued for three days now, and was painfully felt by the couple themselves, as well as by all the members of the family and household.  They felt that there was no sense in their living together and that people who meet accidentally at any inn have more connection with each other than they, the members of the family and household of the Oblonskys.  The wife would not leave her rooms, the husband was away for the third day.  The children were running all over the house as if lost; the English governess quarreled with the housekeeper and wrote a note to a friend, asking her to find her a new place; the cook had already left the premises the day before, at dinner-time; the kitchen-maid and coachman had given notice.
'''
text = '''
Mark who works at Yahoo and John who works at google decided to meet at New York City
'''

# defining callback function for the /start command
def tr(bot, update):
    translator = Translator()
    msg = update.message.text[3:] # delete "/tr "
    msg_tr = translator.translate(msg).text
    bot.send_message(chat_id=update.message.chat_id, text=msg_tr)

# loading the access token from token.txt
#TOKEN = open('token.txt').read().strip()

# call main Telegram objects
#updater = Updater(token=TOKEN)
#dispatcher = updater.dispatcher

# handling callbacks functions to the commands
#dispatcher.add_handler(CommandHandler('tr', tr))

# starting the bot
#updater.start_polling()
import os
print(os.getcwd())

def init():
    pass

def main():
    bc = BertClient(port=5555, port_out=5556)
    with open('../data/questions.csv') as csv_questions:
        readCSV = csv.reader(csv_questions, delimiter=';')
        next(readCSV)
        questions = []
        for line in readCSV:
            questions.append(line[1].rstrip()+'?')

    with open('../data/answers.csv') as csv_answers:
        readCSV = csv.reader(csv_answers, delimiter=';')
        next(readCSV)
        answers = []
        for line in readCSV:
            answers.append(line[1].rstrip())

    print(questions)
    doc_vecs = bc.encode(questions)
    print(doc_vecs)

    topk = 5

    while True:
        query = input('your question: ')
        query_vec = bc.encode([query])[0]
        # compute normalized dot product as score
        score = np.sum(query_vec * doc_vecs, axis=1) / np.linalg.norm(doc_vecs, axis=1)
        topk_idx = np.argsort(score)[::-1][:topk]
        for idx in topk_idx:
            print('> %s\t%s' % (score[idx], questions[idx]))


if __name__ == '__main__':
    main()
