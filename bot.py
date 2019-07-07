import csv
import numpy as np
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from random import randrange
import telegram
import finder
import time
import i18n
from bert_serving.client import BertClient

QUESTIONS_FILE = 'data/questions.csv'
ANSWERS_FILE = 'data/answers.csv'

questions = []
answers = []

first_message = True
language = 'en'
bert_client = BertClient(port=5555, port_out=5556)


def load_questions():
	print('Loading questions...')
	with open(QUESTIONS_FILE) as csv_questions:
		readCSV = csv.reader(csv_questions, delimiter=';')
		next(readCSV)
		for line in readCSV:
			questions.append( (line[1].rstrip(),int(line[0])))

	print('Loading answers...')
	with open(ANSWERS_FILE) as csv_answers:
		readCSV = csv.reader(csv_answers, delimiter=';')
		next(readCSV)
		for line in readCSV:
			answers.append(line[1].rstrip())


def get_lang(update):
	return update.message.from_user.language_code


def rand_str(lang, code):
	n = int(i18n.t("strings.{}.{}-n".format(lang, code)))
	return i18n.t("strings.{}.{}-{}".format(lang, code, randrange(n)))


def com_handler(bot, update):
	text = update.message.text
	print('Original question: {}'.format(text))
	doc_vecs = []
	if first_message:
		global language
		language = update.message.from_user.language_code
		print("First message")
		doc_vecs = bert_client.encode([x[0] for x in questions])
		print("First message")
		global first_question
		first_question = False
	print("Hey")
	query_vec = bert_client.encode([text])[0]
	# compute normalized dot product as score
	topk = 5
	score = np.sum(query_vec * doc_vecs, axis=1) / np.linalg.norm(doc_vecs, axis=1)
	topk_idx = np.argsort(score)[::-1][:topk]
	print(questions[topk_idx[0]][0])
	for idx in topk_idx:
		print('> %s\t%s' % (score[idx], questions[idx]))

	bot.send_message(chat_id=update.message.chat_id, text=questions[topk_idx[0]][0])


def unai(bot, update):
	#bot.send_message(chat_id=update.message.chat_id, text="Hey hola que tal?")
	#bot.send_contact(chat_id=update.message.chat_id, phone_number="112", first_name="Teléfono de emergencias")
	location_keyboard = telegram.KeyboardButton(text=i18n.t("strings.{}.share-loc".format(get_lang(update))), request_location=True)
	custom_keyboard = [[location_keyboard]]
	inline_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=update.message.chat_id, text=rand_str(get_lang(update), "give-location-pls"), reply_markup=inline_markup)


def location(bot, update):
	lang = get_lang(update)
	bot.send_message(chat_id=update.message.chat_id, text=rand_str(lang, "try-find-close-hospital"))
	poi = finder.find(lat=update.message.location.latitude, lng=update.message.location.longitude)
	results = [finder.get_details(poi[i].attrib["id"]) for i in range(0, len(poi))]
	bot.send_message(chat_id=update.message.chat_id, parse_mode=telegram.ParseMode.MARKDOWN,
					text=i18n.t("strings.{}.closest-hospital-is".format(get_lang(update)), name=results[0]["name"]))
	bot.send_location(chat_id=update.message.chat_id, latitude=poi[0].attrib["lat"], longitude=poi[0].attrib["lon"])
	if len(results) > 1:
		time.sleep(1.5 + 0.5 * (len(results) - 1))
		other_options = rand_str(get_lang(update), "other-hospital-options") + "\n"
		for i in results[1:]:
			other_options += "∙ *{}*\n".format(i["name"])
		bot.send_message(chat_id=update.message.chat_id, text=other_options, parse_mode=telegram.ParseMode.MARKDOWN)


#def echo(bot, update):
#	print(update.message)
#	bot.send_message(chat_id=update.message.chat_id, text="Algo\n∙ Algo")


def load_questions():
	print('Loading questions...')
	with open(QUESTIONS_FILE) as csv_questions:
		readCSV = csv.reader(csv_questions, delimiter=';')
		next(readCSV)
		for line in readCSV:
			questions.append( (line[1].rstrip(),int(line[0])))

	print('Loading answers...')
	with open(ANSWERS_FILE) as csv_answers:
		readCSV = csv.reader(csv_answers, delimiter=';')
		next(readCSV)
		for line in readCSV:
			answers.append(line[1].rstrip())


i18n.load_path.append("lang")

# loading the access token from token.txt
TOKEN = open('token.txt').read().strip()

# call main Telegram objects
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

# handling callbacks functions to the commands
dispatcher.add_handler(CommandHandler('unai', unai))
dispatcher.add_handler(CommandHandler('chatbot', com_handler))
dispatcher.add_handler(MessageHandler(Filters.location, location))
dispatcher.add_handler(MessageHandler(Filters.all, com_handler))

load_questions()
doc_vecs = bert_client.encode([x[0] for x in questions])

# starting the bot
updater.start_polling(bootstrap_retries=0)
