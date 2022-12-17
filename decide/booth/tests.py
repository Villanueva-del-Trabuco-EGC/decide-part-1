from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from voting.models import Voting, Question
from django.utils import timezone
from mixnet.models import Auth
from django.conf import settings

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from unittest import mock

from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.models import AbstractBaseUser
from django.test import override_settings
from base.tests import BaseTestCase
from django.urls import reverse
from voting.models import Voting, Question, QuestionOption
from django.utils import timezone
from mixnet.models import Auth
from django.conf import settings
from django.utils.translation import activate

from social_django.models import UserSocialAuth
from social_django.views import get_session_timeout

from base.tests import BaseTestCase


class BoothTranslationTestCase(StaticLiveServerTestCase):

    def setUp(self):
        self.base = BaseTestCase()
        activate('es_ES')
        self.base.setUp()
        super().setUp()    

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

    def testCheckIDTransES(self):
        self.crear_votacion()
        self.driver.get(f'{self.live_server_url}/booth/'+str(self.v_id))
        title = self.driver.find_elements(By.TAG_NAME, 'h1')[1].text
        title = title.split(": ")[0]   
        return self.assertEqual(str(title),'ID de la votación')

    def testCheckNombreTransES(self):
        self.crear_votacion()
        self.driver.get(f'{self.live_server_url}/booth/'+str(self.v_id))
        sub_title = self.driver.find_element(By.TAG_NAME, 'h3').text
        sub_title = sub_title.split(": ")[0]      
        return self.assertEqual(str(sub_title),'Nombre de la votación')

    def testCheckInputsTransES(self):
        self.crear_votacion()
        self.driver.get(f'{self.live_server_url}/booth/'+str(self.v_id))
        inputs = [element.text for element in self.driver.find_elements(By.TAG_NAME, 'label')]
        
        username, password = inputs[0], inputs[1]
        local_check = self.assertEqual(username,"Nombre de usuario")  
        local_check = local_check and self.assertEqual(password,"Contraseña") 
        return local_check
    
    def testCheckLoginTransES(self):
        self.crear_votacion()
        self.driver.get(f'{self.live_server_url}/booth/'+str(self.v_id))
        login = self.driver.find_element(By.TAG_NAME, 'button').text

        return self.assertEqual(login,"Identificarse")

    def testCheckGitHubTransES(self):
        self.crear_votacion()
        self.driver.get(f'{self.live_server_url}/booth/'+str(self.v_id))
        login = self.driver.find_element(By.CLASS_NAME,'btn-secondary').text
        return self.assertEqual(login,"Identificarse con GitHub")  


@override_settings(SOCIAL_AUTH_GITHUB_KEY='1',
                   SOCIAL_AUTH_GITHUB_SECRET='2')
class TestViews(StaticLiveServerTestCase):

    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()
        super().setUp()    

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

    def tearDown(self):
        super().tearDown()
        self.voting = None

    def login_admin(self):
        self.driver.get(f'{self.live_server_url}/admin/login/?next=/admin/')
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()

    def create_voting(self):
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

    def test_backend_exists(self):
        response = self.client.get(reverse('social:begin', kwargs={'backend': 'github'}))
        self.assertEqual(response.status_code, 302)

    def test_backend_not_exists(self):
        url = reverse('social:begin', kwargs={'backend': 'blabla'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_not_logged_booth_view(self):
        v = self.create_voting()
        self.driver.get(f'{self.live_server_url}/booth/'+str(v))
        try:
            githubButton = self.driver.find_element_by_xpath("//a[@id='githubButton']")
            assert True
        except NoSuchElementException:
            assert False

    def test_admin_logged_booth_view(self):
        v = self.create_voting()
        self.login_admin()
        self.driver.get(f'{self.live_server_url}/booth/'+str(v))
        try:
            githubButton = self.driver.find_element_by_xpath("//a[@id='githubButton']")
            assert False
        except NoSuchElementException:
            assert True