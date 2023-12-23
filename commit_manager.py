import os
import time
import requests
import datetime as dt
from dotenv import load_dotenv
from unidecode import unidecode


class CommitManager:

    def __init__(self):
        load_dotenv()
        self.BASE_URL = os.getenv("BASE_URL")
        self.TOKEN = os.getenv("USER_TOKEN")
        self.headers = {
            "X-USER-TOKEN": self.TOKEN}
        self.BASE_GRAPH_URL = f"{self.BASE_URL}/future-/graphs"

    @staticmethod
    def convert_name(user_name):
        converted_name = unidecode(user_name).lower()
        parts = converted_name.split()
        if parts:
            converted_name = parts[0]
        return converted_name

    def create_user(self, user_name):
        post_params = {
            "token": self.TOKEN,
            "username": user_name,
            "agreeTermsOfService": "yes",
            "notMinor": "yes"
        }
        response = requests.post(url=self.BASE_URL, json=post_params)
        print(response.raise_for_status())

    def create_graph(self, user_name):
        converted_name = self.convert_name(user_name)

        graph_params = {
            "id": converted_name,
            "name": f"{converted_name.title()}'s Satisfaction Over Days",
            "unit": "commit",
            "type": "int",
            "color": "sora"
        }

        return self._make_request(
            method=requests.post,
            url=f"{self.BASE_GRAPH_URL}",
            json=graph_params,
            graph_id=converted_name
        )

    def insert_data(self, user_name, user_quantity, max_retries=10, retry_delay=2):
        converted_name = self.convert_name(user_name)
        today = dt.datetime.now()
        insert_date = today.strftime("%Y%m%d")
        graph_params = {
            "date": str(insert_date),
            "quantity": str(user_quantity)
        }
        url = f"{self.BASE_GRAPH_URL}/{converted_name}"

        return self._make_request(
            method=requests.post,
            url=url,
            json=graph_params,
            max_retries=max_retries,
            retry_delay=retry_delay,
            graph_id=converted_name
        )

    def update_data(self, user_name, new_quantity, update_date):
        converted_name = self.convert_name(user_name)
        graph_params = {
            "date": str(update_date),
            "quantity": str(new_quantity)
        }
        url = f"{self.BASE_GRAPH_URL}/{converted_name}/{update_date}"
        return self._make_request(
            method=requests.put,
            url=url,
            json=graph_params,
            graph_id=converted_name
        )

    def delete_data(self, user_name, delete_date):
        converted_name = self.convert_name(user_name)
        url = f"{self.BASE_GRAPH_URL}/{converted_name}/{delete_date}"
        return self._make_request(
            method=requests.delete,
            url=url,
            graph_id=converted_name
        )

    def delete_graph(self, user_name):
        converted_name = self.convert_name(user_name)
        url = f"{self.BASE_GRAPH_URL}/{converted_name}"
        return self._make_request(
            method=requests.delete,
            url=url,
            message="You successfully Deleted graph"
        )

    def _make_request(self, method, url, json=None, max_retries=10, retry_delay=3, graph_id=None, message=None):
        retries = 0
        response = None
        graph_url = f"{self.BASE_GRAPH_URL}/{graph_id}.html"
        while retries < max_retries:
            try:
                response = method(url=url, json=json, headers=self.headers)
                response.raise_for_status()
                return graph_url if graph_id else message
            except requests.exceptions.HTTPError as errh:
                if response is not None and response.status_code == 503:
                    print(f"HTTP Error: {errh}. Retrying...")
                    retries += 1
                    time.sleep(retry_delay)
                else:
                    print(f"HTTP Error: {errh}")
                    return
            except requests.exceptions.ConnectionError as errc:
                print(f"Error Connecting: {errc}")
                return
            except requests.exceptions.Timeout as errt:
                print(f"Timeout Error: {errt}")
                return
            except requests.exceptions.RequestException as err:
                print(f"An unexpected error occurred: {err}")
                return

        return None
