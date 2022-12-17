import random
from time import sleep
from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework.test import APIClient
from .models import Census
from base import mods
from base.tests import BaseTestCase
from census import census_utils as censusUtils
from django.conf import settings
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from django.utils import timezone
from voting.models import Voting, Question, QuestionOption
from mixnet.models import Auth
from django.utils.translation import activate

class CensusTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.census = Census(voting_id=1, voter_id=1)
        self.census.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

    def test_check_vote_permissions(self):
        response = self.client.get('/census/{}/?voter_id={}'.format(1, 2), format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), 'Invalid voter')

        response = self.client.get('/census/{}/?voter_id={}'.format(1, 1), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Valid voter')

    def test_list_voting(self):
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'voters': [1]})

    def test_add_new_voters_conflict(self):
        data = {'voting_id': 1, 'voters': [1]}
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 409)

    def test_add_new_voters(self):
        data = {'voting_id': 2, 'voters': [1,2,3,4]}
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(data.get('voters')), Census.objects.count() - 1)

    def test_destroy_voter(self):
        data = {'voters': [1]}
        response = self.client.delete('/census/{}/'.format(1), data, format='json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(0, Census.objects.count())

class ExportCensusTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.voter_id = User.objects.all().values()[0]['id']
        self.create_voting()
        self.census = Census(voting_id=self.v.id, voter_id=self.voter_id)
        self.census.save()
        self.user_admin = User.objects.filter(username='admin').all()[0]
        self.user_noadmin = User.objects.filter(username='noadmin').all()[0]

    def create_voting(self):
        q = Question(desc="Descripcion")
        q.save()

        opt1 = QuestionOption(question=q,option="opcion1")
        opt1.save()
        opt2 = QuestionOption(question=q,option="opcion2")
        opt2.save()

        self.v = Voting(name="Votacion", question=q)

        self.v.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

    def test_census_utils(self):
        form_values = ['2','4','5']
        selected_atributes = ['id']
        voters_data = []

        census = Census.objects.filter(voting_id=self.v.id).values()
        user_atributes = censusUtils.get_user_atributes()
        data = censusUtils.get_csvtext_and_data(form_values, census)

        for value in form_values:
            atribute = str(user_atributes[int(value)][1])
            selected_atributes.append(atribute)
        self.assertEquals(selected_atributes, data[1]) # headers

        voter = User.objects.filter(id=self.voter_id).values()[0]
        voter_data = []
        for atribute in selected_atributes:
            voter_data.append(str(voter[atribute]))
        voters_data.append(voter_data)
        self.assertEquals(voters_data, data[2]) # atributes values

    def test_access_denied(self):
        self.client.force_login(self.user_noadmin)
        response = self.client.get('/census/export/{}/'.format(self.v.id))
        self.assertEqual(response.status_code, 401)

    def test_access_accepted(self):
        self.client.force_login(self.user_admin)
        response = self.client.get('/census/export/{}/'.format(1), format='json')
        self.assertEqual(response.status_code, 200)

    def test_voting_not_found(self):
        self.client.force_login(self.user_admin)
        voting_id = int(self.v.id) + 1
        response = self.client.get('/census/export/{}/'.format(voting_id), format='json')
        self.assertEqual(response.status_code, 404)

class ExportCensusTransTestCase(StaticLiveServerTestCase):

    def setUp(self):
        self.base = BaseTestCase()
        activate('es_ES')
        self.base.setUp()
        super().setUp()
        self.voter_id = User.objects.all().values()[0]['id']
        self.crear_votacion()
        self.census = Census(voting_id=self.v_id, voter_id=self.voter_id)
        self.census.save()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)


    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()

    def crear_votacion(self):
        q = Question(desc = 'test question')
        q.save()

        v = Voting(name='test voting', question=q)
        v.save()
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.v_id = v.id
        return v.id

    def login_admin(self):
        activate('es_ES')
        self.driver.get(f'{self.live_server_url}/admin/login/?next=/admin/')
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()

    # def testCheckExportName(self):
    #     self.login_admin()
    #     self.driver.get(f'{self.live_server_url}/census/export/{self.v_id}')
    #     activate('es_ES')
    #     self.driver.get(f'{self.live_server_url}/census/export/{self.v_id}')
    #     title = self.driver.find_element(By.TAG_NAME, 'h1').text
    #     title = title.split(": ")[0]
    #     return self.assertEqual(str(title),'Nombre de la votación')

