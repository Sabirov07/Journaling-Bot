from datetime import datetime, timedelta


class ReportManager:
    def __init__(self, db):
        self.db = db

    def _get_weekly_data_query(self, chat_id, end_date=None):
        try:
            if end_date is None:
                end_date = self.db.get_current_date()

            # Convert end_date to datetime object
            end_date = datetime.strptime(end_date, "%d-%m-%Y")

            # Calculate the start date of the week
            start_date = end_date - timedelta(days=(end_date.weekday() + 1) % 7)  # SUNDAY

            # Construct a query to retrieve data for the entire week
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
            if end_date is None:
                end_date = self.db.get_current_date()

            query = self._get_weekly_data_query(chat_id, end_date)
            if query is None:
                return None

            data = list(self.db.counter_collection.find(query))

            if data:
                mood_levels = {}

                for entry in data:
                    date = entry['date']
                    mood_levels[date] = entry.get('mood_score', 0)

                return mood_levels
        except Exception as e:
            print(f"Error in get_mood_levels: {e}")
            return None

    def generate_mood_report(self, chat_id, end_date=None):
        try:
            if end_date is None:
                end_date = self.db.get_current_date()

            mood_levels = self.get_mood_levels(chat_id, end_date)

            if mood_levels:
                total_days = len(mood_levels)
                total_mood_score = sum(mood_levels.values())

                if total_days > 0:
                    average_mood_score = total_mood_score / total_days
                    print("User", chat_id)
                    print("total_days", total_days)
                    print("total_mood_score", mood_levels)
                    print("average_mood_score", average_mood_score)

                    if average_mood_score > 0.1:
                        if average_mood_score >= 7.5:
                            feedback = "😄 You had an outstanding week with excellent mood!\n" \
                                       "Keep spreading the positivity!"
                        elif average_mood_score >= 5.5:
                            feedback = "😊 You had a positive week. Keep striving for happiness."
                        elif average_mood_score >= 3.5:
                            feedback = "😐 You had average mood. Ups and downs happen.\n" \
                                       "Focus on the positive moments."
                        elif average_mood_score >= 1.5:
                            feedback = "😔 Challenging week. Take some time for self-care and reflection."
                        else:
                            feedback = "😢 Tough week. Remember to prioritize self-care and seek support if needed."

                        report_string = f"Mood Report:\n__________________________\n{feedback}"
                        return report_string
        except Exception as e:
            print(f"Error in generate_mood_report: {e}")
            return None

    def get_tasks_number(self, chat_id, end_date=None):
        try:
            if end_date is None:
                end_date = self.db.get_current_date()

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
            print(f"Error in get_tasks_number: {e}")
            return None

    def generate_tasks_report(self, chat_id, end_date=None):
        try:
            if end_date is None:
                end_date = self.db.get_current_date()

            completed_tasks_number, tasks_number = self.get_tasks_number(chat_id, end_date)

            if completed_tasks_number and tasks_number:
                total_completed_tasks = sum(completed_tasks_number.values())
                total_tasks = sum(tasks_number.values())

                if total_tasks:
                    completion_rate = total_completed_tasks / total_tasks

                    # Determine feedback based on completion rate
                    if completion_rate == 1.0:
                        feedback = "🌟 Great job! You completed all your tasks for this week. Keep it up!"
                    elif completion_rate >= 0.8:
                        feedback = "👏 Well done! You completed most of your tasks for this week. " \
                                   "Keep striving for excellence."
                    elif completion_rate >= 0.5:
                        feedback = "🚀 Good effort! You completed more than half of your tasks this week. " \
                                   "Keep improving!"
                    elif completion_rate > 0:
                        feedback = "👍 You made progress! Continue working on completing your tasks for better results."
                    else:
                        feedback = "🚧 No tasks completed yet this week. Time to get started and make progress!"

                    report_string = f"Tasks Report:\n__________________________\nYou completed {total_completed_tasks} tasks out of {total_tasks}" \
                                    f" tasks this week.\n\n{feedback}"

                    return report_string
        except Exception as e:
            print(f"Error in generate_tasks_report: {e}")
            return None

    def get_habits_number(self, chat_id, end_date=None):
        try:
            if end_date is None:
                end_date = self.db.get_current_date()

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

                # Retrieve the total number of habits a user has
                total_habits = self.db.habits_collection.count_documents({"chat_id": chat_id})

                # Calculate the total number of persistent habits for the week
                total_persistent_habits = total_habits * total_days
                # print("total_days", total_days)
                # print("total_habits", total_habits)
                # print("total_persistent_habits", total_persistent_habits)
                # print("completed_habits_number", completed_habits_number)

                return completed_habits_number, total_persistent_habits
        except Exception as e:
            print(f"Error in get_habits_number: {e}")
            return None

    def generate_habits_report(self, chat_id, end_date=None):
        try:
            if end_date is None:
                end_date = self.db.get_current_date()

            completed_habits_number, total_persistent_habits = self.get_habits_number(chat_id, end_date)

            if completed_habits_number and total_persistent_habits:
                total_completed_habits = sum(completed_habits_number.values())

                if total_persistent_habits:
                    # Calculate commitment percentage
                    commitment_percentage = (total_completed_habits / total_persistent_habits) * 100

                    # Provide feedback based on commitment percentage
                    if commitment_percentage == 100:
                        feedback = "🌟 You're absolutely committed! " \
                                   "Fantastic job on completing all your habits this week. " \
                                   "Keep it up!"
                    elif commitment_percentage >= 80:
                        feedback = "👏 Impressive commitment! You're consistently completing your habits. " \
                                   "Keep striving for excellence."
                    elif commitment_percentage >= 50:
                        feedback = "🚀 Good effort! You're making progress in committing to your habits this week. " \
                                   "Keep it up!"
                    elif commitment_percentage > 0:
                        feedback = "🌱 You're on the right track! " \
                                   "Continue working on your habits for better commitment and results."
                    else:
                        feedback = "🕰️ No habits completed yet this week. " \
                                   "It's time to start and make progress towards your habits!"

                    report_string = (
                        f"Habits Report:\n__________________________\n"
                        f"Commitment: {commitment_percentage:.2f}%\n\n"
                        f"You completed {total_completed_habits} commits out of {total_persistent_habits} "
                        f"possible commits toward your habits this week.\n"
                        f"\n\n{feedback}"
                    )

                    return report_string
        except Exception as e:
            print(f"Error in generate_habits_report: {e}")
            return None

    def get_satisfaction_ratings(self, chat_id, end_date=None):
        try:
            if end_date is None:
                end_date = self.db.get_current_date()

            query = self._get_weekly_data_query(chat_id, end_date)
            if query is None:
                return None

            data = list(self.db.ratings_collection.find(query))
            day_ratings = {}
            if data:
                for entry in data:
                    date = entry['date']
                    day_ratings[date] = entry.get('score', 0)

                return day_ratings
        except Exception as e:
            print(f"Error in get_satisfaction_ratings: {e}")
            return None

    def generate_satisfaction_report(self, chat_id, end_date=None):
        try:
            if end_date is None:
                end_date = self.db.get_current_date()

            data = self.get_satisfaction_ratings(chat_id, end_date)
            if data:
                total_days = len(data)
                total_ratings = sum(data.values())
                average_rating = total_ratings / total_days if total_days > 0 else 0
                # print(data)
                # print("total_days", total_days)
                # print("total_ratings", total_ratings)
                # print("average_rating", average_rating)

                if total_days > 0:
                    # Find the most satisfied day
                    most_satisfied_day = max(data, key=data.get)
                    most_satisfied_rating = data[most_satisfied_day]

                    # Organized feedback based on average satisfaction rating
                    if average_rating >= 6.5:
                        feedback = "🌟 Overall, you had an exceptional week with consistently high satisfaction levels. " \
                                   "Well done!"
                    elif average_rating >= 4.5:
                        feedback = "😊 Overall, a positive week with moments of satisfaction. Keep up the good work!"
                    elif average_rating >= 3.5:
                        feedback = "🙂 Overall, your week had a mix of ups and downs, resulting in moderate satisfaction."
                    elif average_rating >= 1.5:
                        feedback = "😐 Overall, there were challenges in your week, leading to varied satisfaction levels. " \
                                   "Reflect and adapt."
                    else:
                        feedback = "😔 Overall, it appears to have been a tough week with lower satisfaction. " \
                                   "Take time for self-care and regroup."

                    report_string = (
                        f"Satisfaction Report of the Week:\n__________________________\n"
                        f"Average satisfaction rating for the week: {average_rating:.2f}\n"
                        f"Most satisfied day: {most_satisfied_day} with a rating of {most_satisfied_rating}\n\n{feedback}"
                    )
                    return report_string
        except Exception as e:
            print(f"Error in generate_satisfaction_report: {e}")
            return None
