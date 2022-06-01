#!/usr/bin/python3

import ast

import aiounittest
import requests_async as requests

from config import TEST_USER_USERNAME, TEST_USER_PASSWORD


class LocalStorage:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = None
        self.socket = 'http://localhost:8000'
        self.user_id = None
        self.email = None
        self.test_investment_item_id = None
        self.test_investment_history_id = None
        self.test_investment_inout_id = None
        self.test_category_id = None
        self.test_key_rate_date = "2019-05-11T12:00:00+00:00"
        self.test_key_rate_value = 7

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


storage = LocalStorage(username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD)


class TestInvestment(aiounittest.AsyncTestCase):
    async def test_investment(self) -> None:
        # refresh token, get user id
        await storage.get_token()

        # test create new investment
        headers = {"Authorization": f"Bearer {storage.token}"}
        params = {"user_id": storage.user_id}
        json = {"description": "test_item", "category_id": None}
        response = await requests.post(f'{storage.socket}/users/investment_items/',
                                       headers=headers, params=params, json=json)
        mydata = ast.literal_eval(response.content.decode("UTF-8").replace("null", "None")
                                  .replace("true", "True").replace("false", "False"))
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
        mydata = ast.literal_eval(response.content.decode("UTF-8").replace("null", "None")
                                  .replace("true", "True").replace("false", "False"))
        new_investment = [d for d in mydata["investments"] if d['id'] == storage.test_investment_item_id][0]
        self.assertTrue(new_investment['description'] == "update_test_item")

        # test delete investment
        params = {"user_id": storage.user_id, "investment_id": storage.test_investment_item_id}
        response = await requests.delete(f'{storage.socket}/users/investment_items/',
                                         headers=headers, params=params)
        mydata = ast.literal_eval(response.content.decode("UTF-8"))
        self.assertTrue(mydata['result'] == "investments deleted")


class TestInvestmentHistory(aiounittest.AsyncTestCase):
    async def test_investment_history(self) -> None:
        # refresh token, get user id
        await storage.get_token()

        # test create new investment
        headers = {"Authorization": f"Bearer {storage.token}"}
        params = {"user_id": storage.user_id}
        json = {"description": "test_item", "category_id": None}
        response = await requests.post(f'{storage.socket}/users/investment_items/',
                                       headers=headers, params=params, json=json)
        mydata = ast.literal_eval(response.content.decode("UTF-8").replace("null", "None")
                                  .replace("true", "True").replace("false", "False"))
        storage.test_investment_item_id = mydata['id']
        self.assertTrue(mydata['description'] == "test_item")

        # test create new investment history
        headers = {"Authorization": f"Bearer {storage.token}"}
        params = {"user_id": storage.user_id}
        json = {"date": "2022-06-01T05:43:50.587Z", "sum": 1000, "investment_id": storage.test_investment_item_id}
        response = await requests.post(f'{storage.socket}/users/investment_history/',
                                       headers=headers, params=params, json=json)
        mydata = ast.literal_eval(response.content.decode("UTF-8").replace("null", "None")
                                  .replace("true", "True").replace("false", "False"))
        storage.test_investment_history_id = mydata['id']
        self.assertTrue(mydata['sum'] == 1000)

        # test update investment history
        headers = {"Authorization": f"Bearer {storage.token}"}
        params = {"user_id": storage.user_id}
        json = {"id": storage.test_investment_history_id, "date": "2022-06-01T05:45:50.587Z", "sum": 2000,
                "investment_id": storage.test_investment_item_id}
        response = await requests.put(f'{storage.socket}/users/investment_history/',
                                      headers=headers, params=params, json=json)
        mydata = ast.literal_eval(response.content.decode("UTF-8"))
        self.assertTrue(mydata['result'] == "investment history updated")

        # test read investment history
        headers = {"Authorization": f"Bearer {storage.token}"}
        params = {"user_id": storage.user_id, "investment_id": storage.test_investment_item_id}
        response = await requests.get(f'{storage.socket}/users/investment_history/',
                                      headers=headers, params=params)
        mydata = ast.literal_eval(response.content.decode("UTF-8").replace("null", "None")
                                  .replace("true", "True").replace("false", "False"))
        new_investment = [d for d in mydata["history"] if d['id'] == storage.test_investment_history_id][0]
        self.assertTrue(new_investment['sum'] == 2000)

        # test delete investment history
        params = {"user_id": storage.user_id, "investment_history_id": storage.test_investment_history_id}
        response = await requests.delete(f'{storage.socket}/users/investment_history/',
                                         headers=headers, params=params)
        mydata = ast.literal_eval(response.content.decode("UTF-8"))
        self.assertTrue(mydata['result'] == "investments history item deleted")

        # test delete investment
        params = {"user_id": storage.user_id, "investment_id": storage.test_investment_item_id}
        response = await requests.delete(f'{storage.socket}/users/investment_items/',
                                         headers=headers, params=params)
        mydata = ast.literal_eval(response.content.decode("UTF-8"))
        self.assertTrue(mydata['result'] == "investments deleted")


class TestInvestmentInOut(aiounittest.AsyncTestCase):
    async def test_investment_inout(self) -> None:
        # refresh token, get user id
        await storage.get_token()

        # test create new investment
        headers = {"Authorization": f"Bearer {storage.token}"}
        params = {"user_id": storage.user_id}
        json = {"description": "test_item", "category_id": None}
        response = await requests.post(f'{storage.socket}/users/investment_items/',
                                       headers=headers, params=params, json=json)
        mydata = ast.literal_eval(response.content.decode("UTF-8").replace("null", "None")
                                  .replace("true", "True").replace("false", "False"))
        storage.test_investment_item_id = mydata['id']
        self.assertTrue(mydata['description'] == "test_item")

        # test create new investment inout
        headers = {"Authorization": f"Bearer {storage.token}"}
        params = {"user_id": storage.user_id}
        json = {"date": "2022-06-01T05:43:50.587Z", "description": "test_inout",
                "sum": 1000, "investment_id": storage.test_investment_item_id}
        response = await requests.post(f'{storage.socket}/users/investment_inout/',
                                       headers=headers, params=params, json=json)
        mydata = ast.literal_eval(response.content.decode("UTF-8").replace("null", "None")
                                  .replace("true", "True").replace("false", "False"))
        storage.test_investment_inout_id = mydata['id']
        self.assertTrue(mydata['sum'] == 1000)

        # test update investment inout
        headers = {"Authorization": f"Bearer {storage.token}"}
        params = {"user_id": storage.user_id}
        json = {"id": storage.test_investment_inout_id, "date": "2022-06-01T05:45:50.587Z", "sum": 2000,
                "description": "updated_inout", "investment_id": storage.test_investment_item_id}
        response = await requests.put(f'{storage.socket}/users/investment_inout/',
                                      headers=headers, params=params, json=json)
        mydata = ast.literal_eval(response.content.decode("UTF-8"))
        self.assertTrue(mydata['result'] == "investment in/out updated")

        # test read investment inout
        headers = {"Authorization": f"Bearer {storage.token}"}
        params = {"user_id": storage.user_id, "investment_id": storage.test_investment_item_id}
        response = await requests.get(f'{storage.socket}/users/investment_inout/',
                                      headers=headers, params=params)
        mydata = ast.literal_eval(response.content.decode("UTF-8").replace("null", "None")
                                  .replace("true", "True").replace("false", "False"))
        new_investment = [d for d in mydata["in_out"] if d['id'] == storage.test_investment_inout_id][0]
        self.assertTrue(new_investment['sum'] == 2000)
        self.assertTrue(new_investment['description'] == "updated_inout")

        # test delete investment inout
        params = {"user_id": storage.user_id, "investment_in_out_id": storage.test_investment_inout_id}
        response = await requests.delete(f'{storage.socket}/users/investment_inout/',
                                         headers=headers, params=params)
        mydata = ast.literal_eval(response.content.decode("UTF-8"))
        self.assertTrue(mydata['result'] == "investments in/out item deleted")

        # test delete investment
        params = {"user_id": storage.user_id, "investment_id": storage.test_investment_item_id}
        response = await requests.delete(f'{storage.socket}/users/investment_items/',
                                         headers=headers, params=params)
        mydata = ast.literal_eval(response.content.decode("UTF-8"))
        self.assertTrue(mydata['result'] == "investments deleted")


class TestCategories(aiounittest.AsyncTestCase):
    async def test_categories(self) -> None:
        # refresh token, get user id
        await storage.get_token()

        # test create new category
        headers = {"Authorization": f"Bearer {storage.token}"}
        params = {"user_id": storage.user_id}
        json = {"category": "test_category"}
        response = await requests.post(f'{storage.socket}/users/categories/',
                                       headers=headers, params=params, json=json)
        mydata = ast.literal_eval(response.content.decode("UTF-8").replace("null", "None")
                                  .replace("true", "True").replace("false", "False"))
        storage.test_category_id = mydata['id']
        self.assertTrue(mydata['category'] == "test_category")

        # test update category
        headers = {"Authorization": f"Bearer {storage.token}"}
        params = {"user_id": storage.user_id}
        json = {"id": storage.test_category_id, "category": "updated_category"}
        response = await requests.put(f'{storage.socket}/users/categories/',
                                      headers=headers, params=params, json=json)
        mydata = ast.literal_eval(response.content.decode("UTF-8"))
        self.assertTrue(mydata['result'] == "category updated")

        # test read category
        headers = {"Authorization": f"Bearer {storage.token}"}
        params = {"user_id": storage.user_id}
        response = await requests.get(f'{storage.socket}/users/categories/',
                                      headers=headers, params=params)
        mydata = ast.literal_eval(response.content.decode("UTF-8").replace("null", "None")
                                  .replace("true", "True").replace("false", "False"))
        new_category = [d for d in mydata["categories"] if d['id'] == storage.test_category_id][0]
        self.assertTrue(new_category['category'] == "updated_category")

        # test delete category
        params = {"user_id": storage.user_id, "category_id": storage.test_category_id}
        response = await requests.delete(f'{storage.socket}/users/categories/',
                                         headers=headers, params=params)
        mydata = ast.literal_eval(response.content.decode("UTF-8"))
        self.assertTrue(mydata['result'] == "category deleted")


class TestKeyRates(aiounittest.AsyncTestCase):
    async def test_key_rates(self) -> None:
        # refresh token, get user id
        await storage.get_token()

        # test read key rates
        headers = {"Authorization": f"Bearer {storage.token}"}
        params = {"user_id": storage.user_id}
        response = await requests.get(f'{storage.socket}/key_rates/',
                                      headers=headers, params=params)
        mydata = ast.literal_eval(response.content.decode("UTF-8").replace("null", "None")
                                  .replace("true", "True").replace("false", "False"))
        key_rates = [d for d in mydata["key_rates"] if d['date'] == storage.test_key_rate_date][0]
        self.assertTrue(key_rates['key_rate'] == storage.test_key_rate_value)


class TestKeyReportsJSON(aiounittest.AsyncTestCase):
    async def test_reports_json(self) -> None:
        # refresh token, get user id
        await storage.get_token()

        # test create new investment
        headers = {"Authorization": f"Bearer {storage.token}"}
        params = {"user_id": storage.user_id}
        json = {"description": "test_report", "category_id": None}
        response = await requests.post(f'{storage.socket}/users/investment_items/',
                                       headers=headers, params=params, json=json)
        mydata = ast.literal_eval(response.content.decode("UTF-8").replace("null", "None")
                                  .replace("true", "True").replace("false", "False"))
        storage.test_investment_item_id = mydata['id']
        self.assertTrue(mydata['description'] == "test_report")

        # test create json report
        headers = {"Authorization": f"Bearer {storage.token}"}
        params = {"user_id": storage.user_id}
        response = await requests.get(f'{storage.socket}/users/reports/json/',
                                      headers=headers, params=params)
        mydata = ast.literal_eval(response.content.decode("UTF-8").replace("null", "None")
                                  .replace("true", "True").replace("false", "False"))
        report = [d for d in mydata["investment_report"] if d['id'] == storage.test_investment_item_id][0]
        self.assertTrue(report["description"] == "test_report")

        # test delete investment
        params = {"user_id": storage.user_id, "investment_id": storage.test_investment_item_id}
        response = await requests.delete(f'{storage.socket}/users/investment_items/',
                                         headers=headers, params=params)
        mydata = ast.literal_eval(response.content.decode("UTF-8"))
        self.assertTrue(mydata['result'] == "investments deleted")
