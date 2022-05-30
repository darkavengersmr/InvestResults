#!/usr/bin/python3

import ast

import aiounittest
import requests_async as requests

from config import TEST_USER_USERNAME, TEST_USER_PASSWORD


class LocalStorage:
    def __init__(self, username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD):
        self.username = username
        self.password = password
        self.token = None
        self.socket = 'http://localhost:8000'
        self.user_id = None
        self.email = None
        self.test_investment_item_id = None

    async def get_token(self) -> None:
        if not self.token:
            data = {'username': self.username, 'password': self.password}
            response = await requests.post(f'{self.socket}/token', data=data)
            mydata = ast.literal_eval(response.content.decode("UTF-8"))
            self.token = mydata['access_token']
        if self.token and not self.user_id:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = await requests.get(f'{self.socket}/user', headers=headers)
            mydata = ast.literal_eval(response.content.decode("UTF-8"))
            self.user_id = mydata['id']
            self.email = mydata['email']


storage = LocalStorage()


class TestApi(aiounittest.AsyncTestCase):
    async def test_create_and_delete_investment(self) -> None:
        # refresh token, get user id
        await storage.get_token()

        # test create new investment
        headers = {"Authorization": f"Bearer {storage.token}"}
        params = {"user_id": storage.user_id}
        json = {"description": "test_item", "category_id": None}
        response = await requests.post(f'{storage.socket}/users/investment_items/',
                                       headers=headers, params=params, json=json)
        mydata = ast.literal_eval(response.content.decode("UTF-8").replace("null", "None"))
        storage.test_investment_item_id = mydata['id']
        self.assertTrue(mydata['description'] == "test_item")

        # test update investment
        headers = {"Authorization": f"Bearer {storage.token}"}
        params = {"user_id": storage.user_id}
        json = {"id": storage.test_investment_item_id, "description": "update_test_item", "category_id": None}
        response = await requests.put(f'{storage.socket}/users/investment_items/',
                                      headers=headers, params=params, json=json)
        mydata = ast.literal_eval(response.content.decode("UTF-8"))
        self.assertTrue(mydata['result'] == "investment updated")

        # test read investment
        headers = {"Authorization": f"Bearer {storage.token}"}
        params = {"user_id": storage.user_id}
        response = await requests.get(f'{storage.socket}/users/investment_items/',
                                      headers=headers, params=params)
        mydata = ast.literal_eval(response.content.decode("UTF-8").replace("null", "None"))
        new_investment = [d for d in mydata["investments"] if d['id'] == storage.test_investment_item_id][0]
        self.assertTrue(new_investment['description'] == "update_test_item")

        # test delete investment
        params = {"user_id": storage.user_id, "investment_id": storage.test_investment_item_id}
        response = await requests.delete(f'{storage.socket}/users/investment_items/',
                                         headers=headers, params=params)
        mydata = ast.literal_eval(response.content.decode("UTF-8"))
        self.assertTrue(mydata['result'] == "investments deleted")
