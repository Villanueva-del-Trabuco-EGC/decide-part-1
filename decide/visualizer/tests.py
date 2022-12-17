import time
from voting.models import QuestionOption, Voting, Question
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from mixnet.models import Auth
from django.conf import settings
from base.tests import BaseTestCase
from django.utils.translation import activate
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User





class VisualizerNavigationTest(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
    
    def test_simpleCorrectLogin(self):
        self.driver.get(f'{self.live_server_url}/admin')
        self.driver.find_element(By.ID,'id_username').send_keys('admin')
        self.driver.find_element(By.ID,'id_password').send_keys('qwerty',Keys.ENTER)

        self.assertTrue(len(self.driver.find_elements(By.ID,'user-tools'))==1)

    def test_simpleWrongLogin(self):
        self.driver.get(f'{self.live_server_url}/admin')
        self.driver.find_element(By.ID,'id_username').send_keys('WRONG')
        self.driver.find_element(By.ID,'id_password').send_keys('WRONG')
        self.driver.find_element(By.ID,'login-form').submit()

        self.assertTrue(len(self.driver.find_elements(By.CLASS_NAME,'errornote'))==1)

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
        v.seats = 3
        v.min_percentage_representation=5
        v.save()

        self.v_id = v.id
        self.voting = v
        return v.id

    def detener_votacion(self):
        v = Voting.objects.get(id=self.v_id)
        v.end_date = timezone.now()
        v.save()

    def test_graphs_dont_exist_nonstarted(self):
        q = Question(desc = 'test question')
        q.save()

        v = Voting(name='test voting', question=q)
        v.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}')
        try:
            title_text = self.driver.find_element(By.ID,'graphs_div').is_displayed()
        except:
            return True
        self.assertTrue(title_text)

    def test_graphs_dont_exist_started(self):
        self.crear_votacion()

        self.driver.get(f'{self.live_server_url}/visualizer/{self.v_id}')
        try:
            title_text = self.driver.find_element(By.ID,'graphs_div').is_displayed()
        except:
            return True
        self.assertTrue(title_text)

    def test_graphs_title_exist(self):
        self.crear_votacion()
        self.detener_votacion()

        self.driver.get(f'{self.live_server_url}/visualizer/{self.v_id}')
        title_text = self.driver.find_element(By.ID,'graphs_title').is_displayed()
        self.assertTrue(title_text)
    
    def test_graph_title_1_exist(self):
        self.crear_votacion()
        self.detener_votacion()

        self.driver.get(f'{self.live_server_url}/visualizer/{self.v_id}')
        title_text = self.driver.find_element(By.ID,'graph_title_1').is_displayed()
        self.assertTrue(title_text)

    def test_graph_title_2_exist(self):
        self.crear_votacion()
        self.detener_votacion()

        self.driver.get(f'{self.live_server_url}/visualizer/{self.v_id}')
        title_text = self.driver.find_element(By.ID,'graph_title_2').is_displayed()
        self.assertTrue(title_text)
        
    def test_graph_title_3_exist(self):
        self.crear_votacion()
        self.detener_votacion()

        self.driver.get(f'{self.live_server_url}/visualizer/{self.v_id}')
        title_text = self.driver.find_element(By.ID,'graph_title_3').is_displayed()
        self.assertTrue(title_text)

    def test_graph_canvas_1_exist(self):
        self.crear_votacion()
        self.detener_votacion()

        self.driver.get(f'{self.live_server_url}/visualizer/{self.v_id}')
        canvas_is_displayed = self.driver.find_element(By.ID,'Graph1').is_displayed()
        self.assertTrue(canvas_is_displayed)

    def test_graph_canvas_2_exist(self):
        self.crear_votacion()
        self.detener_votacion()

        self.driver.get(f'{self.live_server_url}/visualizer/{self.v_id}')
        canvas_is_displayed = self.driver.find_element(By.ID,'Graph2').is_displayed()
        self.assertTrue(canvas_is_displayed)

    def test_graph_canvas_3_exist(self):
        self.crear_votacion()
        self.detener_votacion()

        self.driver.get(f'{self.live_server_url}/visualizer/{self.v_id}')
        canvas_is_displayed = self.driver.find_element(By.ID,'Graph3').is_displayed()
        self.assertTrue(canvas_is_displayed)

class VotingVisualizerTestCase(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()      
            
    def tearDown(self):    
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
        
    def test_noStartVoting_visualizer(self):
        q = Question(desc='test question 1')
        q.save()
        v = Voting(name='test voting 1', question=q, desc='test voting 1')
        v.save()
        
        response =self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        vState= self.driver.find_element(By.TAG_NAME,"h2").text
        self.assertTrue(vState=="Votación no comenzada")
        
        vDesc= self.driver.find_element(By.TAG_NAME,"h3").text
        textoDesc="Descripción de la votación: {}".format(v.desc)
        self.assertTrue(vDesc==textoDesc)
    
    def test_startVoting_visualizer(self):
        q = Question(desc='test question 2')
        q.save()
        date = timezone.now()
        v = Voting(name='test voting 2', question=q, desc='test voting 2',start_date=date)
        v.save()
        
        response =self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        vState= self.driver.find_element(By.TAG_NAME,"h2").text
        self.assertTrue(vState=="Votación en curso")
        
        vDesc= self.driver.find_element(By.TAG_NAME,"h3").text
        textoDesc="Descripción de la votación: {}".format(v.desc)
        self.assertTrue(vDesc==textoDesc)
        
        vDate= self.driver.find_element(By.CLASS_NAME,"inicio").text
        textoFechaInicio="Fecha de inicio de la votación: {}".format(v.start_date.strftime("%d/%m/%Y, %H:%M:%S"))
        self.assertTrue(vDate==textoFechaInicio)

    def test_finishVoting_visualizer(self):
        q = Question(desc='test question 3')
        q.save()
        date = timezone.now()
        v = Voting(name='test voting 3', question=q, desc='test voting 3', start_date=date, end_date=date)
        v.save()
        
        response =self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        vDesc= self.driver.find_element(By.TAG_NAME,"h3").text
        textoDesc="Descripción de la votación: {}".format(v.desc)
        self.assertTrue(vDesc==textoDesc)
        
        vStartDate= self.driver.find_element(By.CLASS_NAME,"inicio").text
        textoFechaInicio="Fecha de inicio de la votación: {}".format(v.start_date.strftime("%d/%m/%Y, %H:%M:%S"))
        self.assertTrue(vStartDate==textoFechaInicio)
        
        vEndDate= self.driver.find_element(By.CLASS_NAME,"fin").text
        textoFechaFin="Fecha de fin de la votación: {}".format(v.end_date.strftime("%d/%m/%Y, %H:%M:%S"))
        self.assertTrue(vEndDate==textoFechaFin)

    def test_postProcVoting_noSeats_visualizer(self):
        q = Question(desc='test question 4')
        q.save()
        date = timezone.now()
        v = Voting(name='test voting 4', question=q, desc='test voting 4', start_date=date, end_date=date)
        v.save()

        response =self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        vDesc= self.driver.find_element(By.TAG_NAME,"h3").text
        textoDesc="Descripción de la votación: {}".format(v.desc)
        
        self.assertTrue(vDesc==textoDesc)
        vStartDate= self.driver.find_element(By.CLASS_NAME,"inicio").text
        textoFechaInicio="Fecha de inicio de la votación: {}".format(v.start_date.strftime("%d/%m/%Y, %H:%M:%S"))
        self.assertTrue(vStartDate==textoFechaInicio)
        
        vEndDate= self.driver.find_element(By.CLASS_NAME,"fin").text
        textoFechaFin="Fecha de fin de la votación: {}".format(v.end_date.strftime("%d/%m/%Y, %H:%M:%S"))
        self.assertTrue(vEndDate==textoFechaFin)

        tipoResultado = self.driver.find_element(By.XPATH,"//table/thead/tr/th[2]").text
        self.assertTrue(tipoResultado=="Puntuación")
    
    def test_postProcVoting_seats_visualizer(self):
        q = Question(desc='test question 5')
        q.save()
        date = timezone.now()
        v = Voting(name='test voting 5', question=q, desc='test voting 5', seats=5, min_percentage_representation=10, start_date=date, end_date=date)
        v.save()
        
        response =self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        vDesc= self.driver.find_element(By.TAG_NAME,"h3").text
        textoDesc="Descripción de la votación: {}".format(v.desc)
        
        self.assertTrue(vDesc==textoDesc)
        vStartDate= self.driver.find_element(By.CLASS_NAME,"inicio").text
        textoFechaInicio="Fecha de inicio de la votación: {}".format(v.start_date.strftime("%d/%m/%Y, %H:%M:%S"))
        self.assertTrue(vStartDate==textoFechaInicio)
        
        vEndDate= self.driver.find_element(By.CLASS_NAME,"fin").text
        textoFechaFin="Fecha de fin de la votación: {}".format(v.end_date.strftime("%d/%m/%Y, %H:%M:%S"))
        self.assertTrue(vEndDate==textoFechaFin)

        tipoResultado = self.driver.find_element(By.XPATH,"//table/thead/tr/th[2]").text
        self.assertTrue(tipoResultado=="Escaños")

        minPercentage = self.driver.find_element(By.CLASS_NAME,"minPercentage").text
        textoMinPercentage="Porcentaje mínimo para tener representación: {}% de los votos totales".format(v.min_percentage_representation)
        self.assertTrue(minPercentage==textoMinPercentage)

class VotingVisualizerTransalationTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        super().setUp()      
            
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
        v.seats = 3
        v.min_percentage_representation=5
        v.save()

        self.v_id = v.id
        self.voting = v
        return v.id

    def detener_votacion(self):
        v = Voting.objects.get(id=self.v_id)
        v.end_date = timezone.now()
        v.save()

    def testCheckIDTransES(self):
        self.crear_votacion()
        self.driver.get(f'{self.live_server_url}/visualizer/'+str(self.v_id))
        ID_text= self.driver.find_elements(By.TAG_NAME, 'h1')[1].text
        ID_text = ID_text.split(":")[0]
        return self.assertEqual(str(ID_text),'ID de la votación')

    def testCheckNombreTransES(self):
        self.crear_votacion()
        self.driver.get(f'{self.live_server_url}/visualizer/'+str(self.v_id))
        Nombre_text= self.driver.find_elements(By.TAG_NAME, 'h1')[2].text
        Nombre_text = Nombre_text.split(":")[0]
        return self.assertEqual(str(Nombre_text),'Nombre de la votación')

    def testCheckResultadosTransES(self):
        self.crear_votacion()
        self.detener_votacion()
        self.driver.get(f'{self.live_server_url}/visualizer/'+str(self.v_id))
        Resultados_text= self.driver.find_elements(By.TAG_NAME, 'h2')[0].text
        return self.assertEqual(str(Resultados_text),'Resultados:')

    def testCheckDescripcionTransES(self):
        self.crear_votacion()
        self.driver.get(f'{self.live_server_url}/visualizer/'+str(self.v_id))
        Desc_text= self.driver.find_elements(By.TAG_NAME, 'h3')[0].text
        Desc_text = Desc_text.split(":")[0]
        return self.assertEqual(str(Desc_text),'Descripción de la votación')
    def testCheckFechaInicioTransES(self):
        self.crear_votacion()
        self.detener_votacion()
        self.driver.get(f'{self.live_server_url}/visualizer/'+str(self.v_id))
        Resultados_text= self.driver.find_elements(By.TAG_NAME, 'h4')[0].text
        Resultados_text=Resultados_text.split(':')[0]
        return self.assertEqual(str(Resultados_text),'Fecha de inicio de la votación')

    def testCheckFechaFinTransES(self):
        self.crear_votacion()
        self.detener_votacion()
        self.driver.get(f'{self.live_server_url}/visualizer/'+str(self.v_id))
        Resultados_text= self.driver.find_elements(By.TAG_NAME, 'h4')[1].text
        Resultados_text=Resultados_text.split(':')[0]
        return self.assertEqual(str(Resultados_text),'Fecha de fin de la votación')

    def testCheckEscañosTransES(self):
        self.crear_votacion()
        self.detener_votacion()
        self.driver.get(f'{self.live_server_url}/visualizer/'+str(self.v_id))
        Resultados_text= self.driver.find_elements(By.TAG_NAME, 'h3')[1].text
        Resultados_text=Resultados_text.split(':')[0]
        return self.assertEqual(str(Resultados_text),'Número de escaños a repartir')

    def testCheckMinPercentageTransES(self):
        self.crear_votacion()
        self.detener_votacion()
        self.driver.get(f'{self.live_server_url}/visualizer/'+str(self.v_id))
        Resultados_text= self.driver.find_elements(By.TAG_NAME, 'h3')[2].text
        Resultados_text=Resultados_text.split(':')[0]
        return self.assertEqual(str(Resultados_text),'Porcentaje mínimo para tener representación')

    def testCheckHontDesTransES(self):
        self.crear_votacion()
        self.detener_votacion()
        self.driver.get(f'{self.live_server_url}/visualizer/'+str(self.v_id))
        Resultados_text= self.driver.find_elements(By.TAG_NAME, 'p')[0].text
        Resultados_text=Resultados_text.split(':')[0]
        return self.assertEqual(str(Resultados_text),"El cálculo en el reparto de escaños esta basado en la Ley D'Hont, en la cual se ignoran las candidaturas con menos del mínimo porcentaje necesario de votos totales, además en caso de empate en el reparto de un escaño, este será dado al candidato con más votos totales obtenidos")

    def testCheckTituloGraficasTransES(self):
        self.crear_votacion()
        self.detener_votacion()
        self.driver.get(f'{self.live_server_url}/visualizer/'+str(self.v_id))
        title_text = self.driver.find_element(By.ID,'graphs_title').text
        self.assertEqual(title_text,'Gráficas de la votación:')
    
    def testCheckTituloGraficas1TransES(self):
        self.crear_votacion()
        self.detener_votacion()
        self.driver.get(f'{self.live_server_url}/visualizer/'+str(self.v_id))
        title_text = self.driver.find_element(By.ID,'graph_title_1').text
        self.assertEqual(title_text,'Gráfica de votos')

    def testCheckTituloGraficas2TransES(self):
        self.crear_votacion()
        self.detener_votacion()
        self.driver.get(f'{self.live_server_url}/visualizer/'+str(self.v_id))
        title_text = self.driver.find_element(By.ID,'graph_title_2').text
        self.assertEqual(title_text,'Gráfica de escaños')
        
    def testCheckTituloGraficas3TransES(self):
        self.crear_votacion()
        self.detener_votacion()
        self.driver.get(f'{self.live_server_url}/visualizer/'+str(self.v_id))
        title_text = self.driver.find_element(By.ID,'graph_title_3').text
        self.assertEqual(title_text,'Gráfica de porcentaje de representación')

class VotingVisualizerTransalationUSTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        self.voter_id = User.objects.all().values()[0]['id']
        self.crear_votacion()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        
        super().setUp()      
            
    def tearDown(self):   
        self.driver.quit()
        activate('es_ES')

        self.base.tearDown()
        super().tearDown()

    def crear_votacion(self):
        q = Question(desc = 'test question')
        q.save()

        opt1 = QuestionOption(question=q,option="opcion1")
        opt1.save()
        opt2 = QuestionOption(question=q,option="opcion2")
        opt2.save()

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
    

    def testCheckDescTransUS(self):
        self.driver.get(f'{self.live_server_url}/visualizer/'+ str(self.v_id))
        self.driver.find_element(By.ID, "id_language_0").click()
        self.driver.find_element(By.ID, "boton_cambiar_idioma").click()
        Desc_text= self.driver.find_elements(By.CSS_SELECTOR, 'h3')[0].text
        Desc_text = Desc_text.split(":")[0]
        self.driver.find_element(By.ID, "id_language_1").click()
        self.driver.find_element(By.ID, "boton_cambiar_idioma").click()
        self.assertTrue(str(Desc_text)=='Description of Voting')
        

    def testCheckNameTransUS(self):
        self.driver.get(f'{self.live_server_url}/visualizer/'+ str(self.v_id))
        self.driver.find_element(By.ID, "id_language_0").click()
        self.driver.find_element(By.ID, "boton_cambiar_idioma").click()
        Name_text= self.driver.find_elements(By.CSS_SELECTOR, 'h1')[2].text
        Name_text = Name_text.split(":")[0]
        self.driver.find_element(By.ID, "id_language_1").click()
        self.driver.find_element(By.ID, "boton_cambiar_idioma").click()
        return self.assertEqual(str(Name_text),'Name of voting')
    
    
