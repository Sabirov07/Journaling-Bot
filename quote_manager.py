import random


class QuoteManager():

    def __init__(self, db):
        self.db = db

    def get_quote(self, chat_id):
        with open("utilities/quotes.txt", encoding='utf-8') as quotes_files:
            quotes = quotes_files.readlines()
            quote = random.choice(quotes)
            self.db.save_quote(chat_id, quote)
            return quote


