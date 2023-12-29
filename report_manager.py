from datetime import datetime, timedelta


class ReportManager:
    def __init__(self, db):
        self.db = db

    def _get_weekly_data_query(self, chat_id, end_date=None):
        try:
            if end_date is None:
                end_date = self.db.get_current_date()

            end_date = datetime.strptime(end_date, "%d-%m-%Y")
            start_date = end_date - timedelta(days=(end_date.weekday() + 1) % 7)  # SUNDAY

            query = {
                'chat_id': chat_id,
                'date': {
                    '$gte': start_date.strftime("%d-%m-%Y"),
                    '$lte': end_date.strftime("%d-%m-%Y")
                }
            }
            return query
        except Exception as e:
            print(f"Error in _get_weekly_data_query: {e}")
            return None

    def get_mood_levels(self, chat_id, end_date=None):
        try:
            query = self._get_weekly_data_query(chat_id, end_date)
            if query is None:
                return None

            data = list(self.db.counter_collection.find(query))

            if data:
                mood_levels = {}
                for entry in data:
                    date = entry['date']
                    mood_levels[date] = entry.get('mood_score', 0)

                return mood_levels if mood_levels else None
        except Exception as e:
            print(f"Error with user {chat_id} in get_mood_levels: {e}")
            return None

    def generate_mood_report(self, chat_id, end_date=None):
        try:
            mood_levels = self.get_mood_levels(chat_id, end_date)

            if mood_levels:
                total_days = len(mood_levels)
                total_mood_score = sum(mood_levels.values())

                if total_days > 0:
                    average_mood_score = total_mood_score / total_days
                    if average_mood_score > 0.1:
                        feedback = self._get_mood_feedback(average_mood_score)

                        report_string = f"Mood Report:\n__________________________\n{feedback}"
                        return report_string
        except Exception as e:
            print(f"Error with user {chat_id} in generate_mood_report: {e}")
            return None

    def _get_mood_feedback(self, average_mood_score):
        try:
            if average_mood_score >= 7.5:
                return "😄 You had an outstanding week with excellent mood!\n" \
                       "Keep spreading the positivity!"
            elif average_mood_score >= 5.5:
                return "😊 You had a positive week. Keep striving for happiness."
            elif average_mood_score >= 3.5:
                return "😐 You had average mood. Ups and downs happen.\n" \
                       "Focus on the positive moments."
            elif average_mood_score >= 1.5:
                return "😔 Challenging week. Take some time for self-care and reflection."
            else:
                return "😢 Tough week. Remember to prioritize self-care and seek support if needed."
        except Exception as e:
            print(f"Error in _get_mood_feedback: {e}")
            return None

    def get_tasks_number(self, chat_id, end_date=None):
        try:
            query = self._get_weekly_data_query(chat_id, end_date)
            if query is None:
                return None

            data = list(self.db.counter_collection.find(query))

            if data:
                completed_tasks_number = {}
                tasks_number = {}

                for entry in data:
                    date = entry['date']
                    completed_tasks_number[date] = entry.get('completed_tasks', 0)
                    tasks_number[date] = entry.get('task_counter', 0)

                return completed_tasks_number, tasks_number
        except Exception as e:
            print(f"Error with user {chat_id} in get_tasks_number: {e}")
            return None

    def generate_tasks_report(self, chat_id, end_date=None):
        try:
            completed_tasks_number, tasks_number = self.get_tasks_number(chat_id, end_date)

            if completed_tasks_number is not None and tasks_number is not None:
                total_completed_tasks = sum(completed_tasks_number.values())
                total_tasks = sum(tasks_number.values())

                if total_tasks:
                    completion_rate = total_completed_tasks / total_tasks

                    feedback = self._get_tasks_feedback(completion_rate)

                    report_string = f"Tasks Report:\n__________________________\n" \
                                    f"You completed {total_completed_tasks} tasks out of {total_tasks}" \
                                    f" tasks this week.\n\n{feedback}"

                    return report_string
                else:
                    print(f"No task data available for the {chat_id} user .")
                    return None
            else:
                print("Error retrieving task data. Please try again later.")
                return

        except Exception as e:
            print(f"Error with user {chat_id} in generate_tasks_report: {e}")
            return None

    def _get_tasks_feedback(self, completion_rate):
        try:
            if completion_rate == 1.0:
                return "🌟 Great job! You completed all your tasks for this week. Keep it up!"
            elif completion_rate >= 0.8:
                return "👏 Well done! You completed most of your tasks for this week. " \
                       "Keep striving for excellence."
            elif completion_rate >= 0.5:
                return "🚀 Good effort! You completed more than half of your tasks this week. " \
                       "Keep improving!"
            elif completion_rate > 0:
                return "👍 You made progress! Continue working on completing your tasks for better results."
            else:
                return "🚧 No tasks completed yet this week. Time to get started and make progress!"
        except Exception as e:
            print(f"Error in _get_tasks_feedback: {e}")
            return None

    def get_habits_number(self, chat_id, end_date=None):
        try:
            query = self._get_weekly_data_query(chat_id, end_date)
            if query is None:
                return None

            data = list(self.db.counter_collection.find(query))

            if data:
                completed_habits_number = {}

                for entry in data:
                    date = entry["date"]
                    completed_habits_number[date] = entry.get("completed_habits", 0)

                total_days = len(completed_habits_number)

                total_habits = self.db.habits_collection.count_documents({"chat_id": chat_id})

                total_persistent_habits = total_habits * total_days

                return completed_habits_number, total_persistent_habits
        except Exception as e:
            print(f"Error with user {chat_id} in get_habits_number: {e}")
            return None

    def generate_habits_report(self, chat_id, end_date=None):
        try:
            completed_habits_number, total_possible_commits = self.get_habits_number(chat_id, end_date)

            if completed_habits_number is not None and total_possible_commits is not None:
                total_completed_habits = sum(completed_habits_number.values())

                if total_possible_commits:
                    commitment_percentage = (total_completed_habits / total_possible_commits) * 100

                    feedback = self._get_habits_feedback(commitment_percentage)

                    report_string = (
                        f"Habits Report:\n__________________________\n"
                        f"Commitment: {commitment_percentage:.2f}%\n\n"
                        f"You completed {total_completed_habits} commits out of {total_possible_commits} "
                        f"possible commits toward your habits this week.\n"
                        f"\n\n{feedback}"
                    )

                    return report_string
                else:
                    print(f"No habit data available for the {chat_id} user .")
                    return None
            else:
                print("Error retrieving habit data. Please try again later.")
                return None

        except Exception as e:
            print(f"Error with user {chat_id} in generate_habits_report: {e}")
            return None



    def _get_habits_feedback(self, commitment_percentage):
        try:
            if commitment_percentage == 100:
                return "🌟 You're absolutely committed! " \
                       "Fantastic job on completing all your habits this week. " \
                       "Keep it up!"
            elif commitment_percentage >= 80:
                return "👏 Impressive commitment! You're consistently completing your habits. " \
                       "Keep striving for excellence."
            elif commitment_percentage >= 50:
                return "🚀 Good effort! You're making progress in committing to your habits this week. " \
                       "Keep it up!"
            elif commitment_percentage > 0:
                return "🌱 You're on the right track! " \
                       "Continue working on your habits for better commitment and results."
            else:
                return "🕰️ No habits completed yet this week. " \
                       "It's time to start and make progress towards your habits!"
        except Exception as e:
            print(f"Error in _get_habits_feedback: {e}")
            return None

    def get_satisfaction_ratings(self, chat_id, end_date=None):
        try:
            query = self._get_weekly_data_query(chat_id, end_date)
            if query is None:
                return None

            data = list(self.db.ratings_collection.find(query))
            day_ratings = {}

            if data:
                for entry in data:
                    date = entry['date']
                    day_ratings[date] = entry.get('score', 0)

                return day_ratings if day_ratings else None
        except Exception as e:
            print(f"Error with user {chat_id} in get_satisfaction_ratings: {e}")
            return None

    def generate_satisfaction_report(self, chat_id, end_date=None):
        try:
            data = self.get_satisfaction_ratings(chat_id, end_date)

            if data:
                total_days = len(data)
                total_ratings = sum(data.values())
                average_rating = total_ratings / total_days if total_days > 0 else 0

                if average_rating > 0.1:
                    most_satisfied_day = max(data, key=data.get)
                    most_satisfied_rating = data[most_satisfied_day]

                    feedback = self._get_satisfaction_feedback(average_rating)

                    report_string = (
                        f"Satisfaction Report of the Week:\n__________________________\n"
                        f"Average satisfaction rating for the week: {average_rating:.2f}\n"
                        f"Most satisfied day: {most_satisfied_day} with a rating of {most_satisfied_rating}\n\n{feedback}"
                    )
                    return report_string
        except Exception as e:
            print(f"Error with user {chat_id} in generate_satisfaction_report: {e}")
            return None

    def _get_satisfaction_feedback(self, average_rating):
        try:
            if average_rating >= 6.5:
                return "🌟 Overall, you had an exceptional week with consistently high satisfaction levels. " \
                       "Well done!"
            elif average_rating >= 4.5:
                return "😊 Overall, a positive week with moments of satisfaction. Keep up the good work!"
            elif average_rating >= 3.5:
                return "🙂 Overall, your week had a mix of ups and downs, resulting in moderate satisfaction."
            elif average_rating >= 1.5:
                return "😐 Overall, there were challenges in your week, leading to varied satisfaction levels. " \
                       "Reflect and adapt."
            else:
                return "😔 Overall, it appears to have been a tough week with lower satisfaction. " \
                       "Take time for self-care and regroup."
        except Exception as e:
            print(f"Error in _get_satisfaction_feedback: {e}")
            return None
