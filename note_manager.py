from telegram import Update
from telegram.ext import CallbackContext


class NoteManager:
    def __init__(self, db):
        self.db = db

    async def add_note(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        context.user_data[chat_id] = {'state': 'add_note'}
        await update.message.reply_text('Please write the note of the day.')

    async def handle_add_note(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        note_content = update.message.text.strip()

        note_id = self.db.save_note(chat_id, note_content)

        context.user_data[chat_id]['state'] = ''
        await update.message.reply_text(f"Note №:{note_id} was added.")

    async def show_notes(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id

        notes = self.db.get_notes(chat_id)

        if notes:
            note_content = "\n".join([f"{note['id']}. {note['content']}" for note in notes])
            notes_message = "Today's notes📝:\n__________________________\n" + note_content

            await update.message.reply_text(notes_message)
        else:
            await update.message.reply_text("You do not have any notes!")

    async def delete_note(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id

        notes = self.db.get_notes(chat_id)
        if notes:
            context.user_data[chat_id] = {'state': 'delete_note'}
            notes_text = "\n".join([f"{note['id']}. {note['content']}" for note in notes])
            await update.message.reply_text(f"Your notes:\n{notes_text}\n\n"
                                            "Enter the ID of the note you want to delete.")
        else:
            await update.message.reply_text("No notes found.")

    async def handle_delete_note(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        user_input = update.message.text.strip()

        try:
            note_id = int(user_input)
            note = self.db.note_exists(chat_id, note_id)

            if note:
                self.db.delete_note(chat_id, note_id)
                context.user_data[chat_id]['state'] = ''
                await update.message.reply_text(f"The note №:{note_id} has been removed!")
            else:
                context.user_data[chat_id] = {'state': 'delete_note'}
                await update.message.reply_text("Please choose a valid ID from the list👆🏿")
        except ValueError:
            context.user_data[chat_id] = {'state': 'delete_note'}
            await update.message.reply_text("Invalid input. Please enter a valid note ID number.")
