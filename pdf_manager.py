import os
import io
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfWriter, PdfReader


script_directory = os.path.dirname(os.path.realpath(__file__))
font_path = os.path.join(script_directory, 'Fonts')

# Load the fonts
pdfmetrics.registerFont(TTFont('Symbola', os.path.join(font_path, 'Symbola.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuSans', os.path.join(font_path, 'DejaVuSans.ttf')))


class PDFManager:

    def __init__(self, db):
        self.db = db
        self.packet = io.BytesIO()
        self.can = canvas.Canvas(self.packet, pagesize=letter)
        self.can.setFont("DejaVuSans", 11)
        self.output_folder = os.path.join(script_directory, 'OutputPDFs')

    @staticmethod
    def split_note(long_text, max_line_length=32):
        words = long_text.split()
        lines = []
        current_line = " "

        for word in words:
            if len(current_line) + len(word) + 1 <= max_line_length:
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "

        lines.append(current_line.strip())
        result = "\n".join(lines)
        return result

    def pdf_write(self, chat_id, user_name):
        user_tasks = self.db.get_tasks(chat_id)
        if user_tasks:
            action_tasks = [
                f"●  {task['description']}"
                for task in user_tasks
                if 'completed' not in task or not task['completed']]
            completed_tasks = [
                f"●  {task['description']} ✔  ({task.get('time', 'N/A')})"
                for task in user_tasks
                if 'completed' in task and task['completed']
            ]
            completed_tasks.extend(action_tasks)
            self.write_down(54, 621, completed_tasks)

        user_habits = self.db.get_habits(chat_id)
        if user_habits:
            habits_list = [
                f"●  {habit['description']}"
                for habit in user_habits
                if 'completed' not in habit or not habit['completed']]
            completed_habits = [
                f"●  {habit['description']} ✔  ({habit.get('time', 'N/A')})"
                for habit in user_habits
                if 'completed' in habit and habit['completed']
            ]
            completed_habits.extend(habits_list)
            self.write_down(54, 165, completed_habits)

        user_notes = self.db.get_notes(chat_id)
        if user_notes:  # Check if the list is not empty
            note_list = [f"●  {note['content']}    ({note['time']})" for note in user_notes]
            self.write_down(336, 621, note_list)

        user_quote = self.db.get_quote(chat_id)
        if user_quote:
            quote = user_quote[0].get('quote', '')
            self.insert_quote(336, 165, quote)

        user_mood = self.db.get_mood(chat_id)
        if user_mood:
            mood = user_mood[0].get('mood', '')
            self.insert_emoji(374, 758, mood)

        user_rating = self.db.get_rating(chat_id)
        if user_rating:
            score = user_rating[0].get('score', '')
            self.insert_score(515, 758, score)

        user_state = self.db.get_state(chat_id)
        if user_state:
            print("Got user state", user_state)
            self.insert_state(115, 28, user_state)

        output_filename = self.locate_inputs(user_name)
        return output_filename

    def write_down(self, x, y, user_input_list):
        y_coordinate = y
        for user_input in user_input_list:
            x_coordinate = x
            if len(user_input) > 38:
                lines = self.split_note(user_input, max_line_length=37)
                first_line_inserted = False

                for line in lines.splitlines():
                    if not first_line_inserted:
                        self.can.drawString(x, y_coordinate, line)
                        first_line_inserted = True
                        x_coordinate += 13
                    else:
                        self.can.drawString(x_coordinate, y_coordinate, line)
                    y_coordinate -= 20
            else:
                self.can.drawString(x, y_coordinate, user_input)
                y_coordinate -= 20

    def insert_emoji(self, x, y, emoji):
        self.can.setFont("Symbola", 16)
        self.can.drawString(x, y, emoji)

    def insert_score(self, x, y, score):
        self.can.setFont("DejaVuSans", 16)
        self.can.drawString(x, y, str(score))

    def insert_state(self, x, y, state):
        self.can.setFont("DejaVuSans", 10)
        self.can.drawString(x, y, state)

    def insert_quote(self, x, y, quote):
        self.can.setFont("DejaVuSans", 11)
        text_object = self.can.beginText(x, y)

        written_quote = self.split_note(quote)

        for line in written_quote.splitlines():
            text_object.textLine(line)

        self.can.drawText(text_object)

    def locate_inputs(self, user_name):
        self.can.setFont("DejaVuSans", 14)
        self.can.drawString(373, 707, datetime.now().strftime("%d / %b / %Y   (%a)"))

        self.can.save()

        self.packet.seek(0)

        existing_pdf = PdfReader(open("utilities/day.pdf", "rb"))

        new_pdf = PdfWriter()

        page = existing_pdf.pages[0]
        page.merge_page(PdfReader(self.packet).pages[0])
        new_pdf.add_page(page)

        timestamp = datetime.now().strftime("%d_%m_%Y (%M-%S)")
        output_filename = os.path.join(self.output_folder, f"{user_name} {timestamp}.pdf")

        # Write the output to the new PDF file
        with open(output_filename, "wb") as output_stream:
            new_pdf.write(output_stream)

        print(f"PDF saved as {output_filename}")

        return output_filename


