from pymongo import MongoClient
from datetime import datetime


class DatabaseManager:

    def __init__(self, db_url):
        self.client = MongoClient(db_url)
        self.db = self.client['journalDB']

        # Collections
        self.users_collection = self.db['users']
        self.tasks_collection = self.db['tasks']
        self.notes_collection = self.db['notes']
        self.moods_collection = self.db['moods']
        self.habits_collection = self.db['habits']
        self.quotes_collection = self.db['quotes']
        self.graphs_collection = self.db['graphs']
        self.counter_collection = self.db['counters']
        self.journal_collection = self.db['journals']
        self.ratings_collection = self.db['day_ratings']

    @staticmethod
    def get_current_date():
        return datetime.now().strftime("%d-%m-%Y")

    ## TASK DB
    def save_task(self, chat_id, task_description, date=None):
        if date is None:
            date = self.get_current_date()

        order_id = self._get_next_order_id(chat_id, 'task', date=date)
        task_doc = {
            'id': order_id,
            'chat_id': chat_id,
            'description': task_description,
            'completed': False,
            'date': date
        }
        self.tasks_collection.insert_one(task_doc)
        return order_id

    def get_tasks(self, chat_id):
        date = self.get_current_date()
        return list(self.tasks_collection.find({'chat_id': chat_id, 'date': date}))

    def complete_task(self, chat_id, task_id, date=None):
        if date is None:
            date = self.get_current_date()
        completion_time = datetime.now().strftime("%H:%M")
        self.tasks_collection.update_one(
            {'chat_id': chat_id, 'id': task_id, 'date': date},
            {'$set': {'completed': True, 'time': completion_time}}
        )
        counter_doc = self.counter_collection.find_one_and_update(
            {"chat_id": chat_id, "date": date},
            {"$inc": {"completed_tasks": 1}},
            upsert=True,
            return_document=True,
        )
        if not counter_doc:
            counter_doc = {"chat_id": chat_id, "date": date, "completed_tasks": 1}
            self.counter_collection.insert_one(counter_doc)

    def delete_task(self, chat_id, task_id):
        date = self.get_current_date()
        self.tasks_collection.delete_one({'chat_id': chat_id, 'id': task_id, 'date': date})

    def task_exists(self, chat_id, task_id):
        date = self.get_current_date()
        return self.tasks_collection.find_one(
            {'chat_id': chat_id, 'id': task_id, 'date': date}) is not None

    ## NOTE DB
    def save_note(self, chat_id, content, date=None):
        if date is None:
            date = self.get_current_date()

        order_id = self._get_next_order_id(chat_id, 'note', date=date)
        note_doc = {
            'id': order_id,
            'chat_id': chat_id,
            'content': content,
            'time': datetime.now().strftime("%H:%M"),
            'date': date
        }
        self.notes_collection.insert_one(note_doc, date)
        return order_id

    def get_notes(self, chat_id):
        date = self.get_current_date()
        return list(self.notes_collection.find({'chat_id': chat_id, 'date': date}))

    def delete_note(self, chat_id, note_id):
        current_date = datetime.now().strftime("%d-%m-%Y")
        self.notes_collection.delete_one({'chat_id': chat_id, 'id': note_id, 'date': current_date})

    def note_exists(self, chat_id, note_id):
        date = self.get_current_date()
        return self.notes_collection.find_one(
            {'chat_id': chat_id, 'id': note_id, 'date': date}) is not None

    ## HABIT DB
    def save_habit(self, chat_id, habit_description, date=None):
        if date is None:
            date = self.get_current_date()

        order_id = self._get_next_habit_id(chat_id)
        habit_doc = {
            'id': order_id,
            'chat_id': chat_id,
            'description': habit_description,
            'completed': False,
            'date': date
        }
        self.habits_collection.insert_one(habit_doc)

        return order_id

    def get_habits(self, chat_id):
        return list(self.habits_collection.find({'chat_id': chat_id}))

    def complete_habit(self, chat_id, habit_id, date=None):
        if date is None:
            date = self.get_current_date()
        completion_time = datetime.now().strftime("%H:%M")

        # Update habit completion in habits_collection
        result = self.habits_collection.update_one(
            {'chat_id': chat_id, 'id': habit_id},
            {'$set': {'completed': True, 'time': completion_time}}
        )

        # Update completed habits counter in counter_collection for the specific date
        counter_doc = self.counter_collection.find_one_and_update(
            {"chat_id": chat_id, "date": date},
            {"$inc": {"completed_habits": 1}},
            upsert=True,
            return_document=True,
        )

        if not counter_doc:
            counter_doc = {"chat_id": chat_id, "date": date, "completed_habits": 1}
            self.counter_collection.insert_one(counter_doc)

        return result

    def uncomplete_habits(self, chat_id):
        self.habits_collection.update_many(
            {'chat_id': chat_id},
            {'$set': {'completed': False}},
        )

    def delete_habit(self, chat_id, habit_id):
        self.habits_collection.delete_one({'chat_id': chat_id, 'id': habit_id})

    def habit_exists(self, chat_id, habit_id):
        return self.habits_collection.find_one({'chat_id': chat_id, 'id': habit_id}) is not None

    ## QUOTE DB
    def save_quote(self, chat_id, quote, date=None):
        if date is None:
            date = self.get_current_date()

        existing_quote = self.quotes_collection.find_one({'chat_id': chat_id, 'date': date})

        if existing_quote:
            self.quotes_collection.delete_one({'chat_id': chat_id, 'date': date})

        quote_doc = {
            'chat_id': chat_id,
            'quote': quote,
            'date': date
        }
        self.quotes_collection.insert_one(quote_doc)

    def get_quote(self, chat_id, date=None):
        if date is None:
            date = self.get_current_date()
        query = {'chat_id': chat_id, 'date': date}
        return list(self.quotes_collection.find(query))

    # RATING DB
    def save_rating(self, chat_id, score, date=None):
        if date is None:
            date = self.get_current_date()
        existing_rating = self.ratings_collection.find_one({'chat_id': chat_id, 'date': date})

        if existing_rating:
            self.ratings_collection.delete_one({'chat_id': chat_id, 'date': date})

        rating_doc = {
            'chat_id': chat_id,
            'score': score,
            'date': date
        }
        self.ratings_collection.insert_one(rating_doc)

    def get_rating(self, chat_id, date=None):
        if date is None:
            date = self.get_current_date()
        query = {'chat_id': chat_id, 'date': date}
        return list(self.ratings_collection.find(query))

    #MOOD DB
    def save_mood(self, chat_id, mood, mood_score, date=None):
        if date is None:
            date = self.get_current_date()

        existing_mood = self.moods_collection.find_one({'chat_id': chat_id, 'date': date})

        if existing_mood:
            self.moods_collection.delete_one({'chat_id': chat_id, 'date': date})

        mood_doc = {
            'chat_id': chat_id,
            'mood': mood,
            'date': date
        }
        self.moods_collection.insert_one(mood_doc)

        counter_doc = self.counter_collection.find_one_and_update(
            {"chat_id": chat_id, "date": date},
            {"$set": {"mood_score": mood_score}},
            upsert=True,
            return_document=True,
        )
        if not counter_doc:
            counter_doc = {"chat_id": chat_id, "mood_score": mood_score, "date": date}
            self.counter_collection.insert_one(counter_doc)

    def get_mood(self, chat_id, date=None):
        if date is None:
            date = self.get_current_date()
        query = {'chat_id': chat_id, 'date': date}
        return list(self.moods_collection.find(query))

    def save_graph(self, chat_id, user_name, graph, date=None):
        if date is None:
            date = self.get_current_date()
        graph_doc = {
            'chat_id': chat_id,
            'user_name': user_name,
            'graph': graph,
            'date': date
        }
        self.graphs_collection.insert_one(graph_doc)
        self.add_graph(chat_id, graph)

    def get_graph(self, chat_id):
        return self.graphs_collection.find_one({'chat_id': chat_id}) is not None

    def save_user(self, chat_id, user_name):
        user_exists = self.users_collection.find_one({'chat_id': chat_id})
        if not user_exists:
            user_doc = {
                'chat_id': chat_id,
                'user_name': user_name
            }
            self.users_collection.insert_one(user_doc)

    def get_all_users(self):
        result = self.users_collection.find({}, {'chat_id': 1, 'user_name': 1, '_id': 0})
        return result

    def add_graph(self, chat_id, graph):
        self.users_collection.find_one_and_update(
            {'chat_id': chat_id},
            {'$set': {'user_graph': graph}},
            upsert=True)

    def add_state(self, chat_id, state_description):
        self.users_collection.find_one_and_update(
            {'chat_id': chat_id},
            {'$set': {'state': state_description}},
            upsert=True
        )

    def get_state(self, chat_id):
        user = self.users_collection.find_one({'chat_id': chat_id})
        if user:
            return user.get('state', '')
        else:
            return None

    def save_pdf(self, chat_id, user_name, pdf_data, filename):
        date = self.get_current_date()

        existing_pdf = self.journal_collection.find_one({'chat_id': chat_id, 'user_name': user_name, 'date': date})

        if existing_pdf:
            self.journal_collection.update_one(
                {'chat_id': chat_id, 'user_name': user_name, 'date': date},
                {'$set': {'filename': filename, 'pdf_data': pdf_data}}
            )
            # print(f"PDF updated in the database for {user_name} at {date} with filename: {filename}")
        else:
            pdf_document = {
                'chat_id': chat_id,
                'user_name': user_name,
                'filename': filename,
                'pdf_data': pdf_data,
                'date': date,
            }
            self.journal_collection.insert_one(pdf_document)
            # print(f"PDF saved to the database for {user_name} at {date} with filename: {filename}")

    def _get_next_order_id(self, chat_id, collection_name, date=None):
        if date is None:
            date = self.get_current_date()

        counter_doc = self.counter_collection.find_one_and_update(
            {"chat_id": chat_id, "date": date},
            {"$inc": {f"{collection_name}_counter": 1}},
            upsert=True,
            return_document=True,
        )

        if not counter_doc:
            counter_doc = {"chat_id": chat_id, f"{collection_name}_counter": 1, "date": date}
            self.counter_collection.insert_one(counter_doc)

        return counter_doc[f"{collection_name}_counter"]

    def _get_next_habit_id(self, chat_id):
        counter_doc = self.counter_collection.find_one_and_update(
            {"chat_id": f"User {chat_id}"},
            {"$inc": {"user_habits": 1}},
            upsert=True,
            return_document=True,
        )

        if not counter_doc:
            counter_doc = {"chat_id": f"User {chat_id}", "user_habits": 1}
            self.counter_collection.insert_one(counter_doc)

        return counter_doc["user_habits"]
