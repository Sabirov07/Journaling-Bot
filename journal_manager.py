from telegram import Update
from telegram.ext import CallbackContext
from commit_manager import CommitManager
from pdf_manager import PDFManager


class JournalManager:
    def __init__(self, db):
        self.db = db
        self.commit_manager = CommitManager()

    async def handle_add_rating(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        user_rating_number = update.message.text.strip()

        try:
            rating = int(user_rating_number)

            if 1 <= rating <= 10:
                context.user_data[chat_id]['state'] = ''
                await update.message.reply_text("Wait, your Journal PDF is on the way...")
                self.db.save_rating(chat_id, rating)
                await self.pdf_write(update, context)
                await self.insert_rating(update, rating)
                self.db.uncomplete_habits(chat_id)
                return
            else:
                context.user_data[chat_id] = {'state': 'day_rating'}
                await update.message.reply_text("Please enter a rating between 1 and 10.")
                return
        except ValueError as e:
            context.user_data[chat_id] = {'state': 'day_rating'}
            await update.message.reply_text("Please enter a NUMBER between 1 and 10.")
            return

    async def pdf_write(self, update: Update, context: CallbackContext):
        pdf_manager = PDFManager(self.db)
        chat_id = update.message.chat_id
        user_name = update.message.from_user.first_name

        #We extract value of the pdf touple returned by pdf_write
        pdf_data, filename = pdf_manager.pdf_write(chat_id, user_name)

        await context.bot.send_document(chat_id=chat_id, document=pdf_data, filename=filename)

        print("PDF sent to user:", user_name)

    async def insert_rating(self, update: Update, score):
        chat_id = update.message.chat_id
        user_name = update.message.from_user.first_name

        graph = self.db.get_graph(chat_id)

        if not graph:
            graph = self.commit_manager.create_graph(user_name)
            if graph:
                self.db.save_graph(chat_id, user_name, graph)
        link = self.commit_manager.insert_data(user_name, score)
        if link:
            message = f"🔗 [{user_name}'s Commitment Table]({link})."
            await update.message.reply_text(message, parse_mode='Markdown',
                                            disable_web_page_preview=True)

    async def add_state(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        state_description = update.message.text.strip().replace('\n', ' ')

        self.db.add_state(chat_id, state_description)

        context.user_data[chat_id]['state'] = ''
        await update.message.reply_text(f"Your temporary state was set!"
                                        f"\nYou can change it anytime with /state")


