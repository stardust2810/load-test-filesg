from locust import HttpUser, task, between, TaskSet, LoadTestShape, events
import json, string, secrets
import logging, sys
import csv
import requests

requests.packages.urllib3.disable_warnings() 
ACCOUNTS = None

class PortalAccess(TaskSet):
	current_user = 'NOT FOUND'
	nonce = 'NOT FOUND'

	def on_start(self):
		self.client.verify = False
		if len(ACCOUNTS) > 0:
			logging.info(ACCOUNTS)
			self.current_user, self.nonce = ACCOUNTS.pop()
		else:
			logging.info("No more accounts, reverting to default account S3002610A")
			self.current_user = 'S3002610A'


		#1 go to dev.file.gov.sg
		#create CSRF token and put into cookie
		csrf_token = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		self.client.cookies.set('filesg-csrf-id', csrf_token)
		logging.info('[%s] Go to home page====================',self.current_user)
		with self.client.post('/', headers={'accept':'application/json, text/plain, */*','content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36','cookie':'filesg-csrf-id='+csrf_token}, catch_response=True, verify=False ) as response:
			logging.debug(response.status_code)
			logging.debug(response.cookies)
			#logging.debug("[Dict] +++++++++++++++++++++++++")
			#logging.debug(self.client.cookies.get_dict())

		#2 call get user details to create a session, should return csrf, filesg_cookie
		logging.info('[%s] Get user session====================',self.current_user)
		with self.client.get('https://www.dev.file.gov.sg/core/auth/user-session-details', headers={'authority':'www.dev.file.gov.sg','accept':'application/json, text/plain, */*','user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36','x-csrf-token':csrf_token,'cookie':'filesg-csrf-id='+csrf_token}, catch_response=True, name='get-session', verify=False ) as response:
			logging.debug(response.status_code)
			logging.debug(response.cookies)
			#logging.debug("[Dict] +++++++++++++++++++++++++")
			#logging.debug(self.client.cookies.get_dict())

		#3 call mock login with payload which returns filesg_cookie
		logging.info('[%s] Mock Login====================',self.current_user)
		#request_body = {'authCode':'S3002610A','nonce':'mock'}
		request_body = {'authCode':self.current_user,'nonce':'mock'}
		with self.client.post('/core/auth/mock-login', json=request_body, headers={'accept':'application/json, text/plain, */*','content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}, catch_response=True, name='mock-login', verify=True ) as response:
			logging.debug(response.status_code)
			logging.debug(response.cookies)
			#logging.debug("[Dict] +++++++++++++++++++++++++")
			#logging.debug(self.client.cookies.get_dict())

		#4 call get user details (get new session), should return csrf, filesg_cookie
		#print("[4] Get user details again===================")


		#5 call activities
		logging.info('[%s] Get activities====================',self.current_user)
		with self.client.get('/core/transaction/activities?sortBy=createdAt&asc=false&page=1&limit=3', headers={'accept':'application/json, text/plain, */*','content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}, catch_response=True, name='dashboard/activities', verify=False ) as response:
			logging.debug(response.status_code)
			logging.debug(response.cookies)
			#logging.debug("[Dict] +++++++++++++++++++++++++")
			#logging.debug(self.client.cookies.get_dict())
			#print(response.text)	

		#6 call files
		logging.info('[%s] Get files====================',self.current_user)
		with self.client.get('/core/file/all-files?sortBy=lastViewedAt&asc=false&page=1&limit=5&statuses=active,expired,revoked&ignoreNull=true', headers={'accept':'application/json, text/plain, */*','content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}, catch_response=True, name='dashboard/files', verify=False ) as response:
			logging.debug(response.status_code)
			logging.debug(response.cookies)
			#logging.debug("[Dict] +++++++++++++++++++++++++")
			#logging.debug(self.client.cookies.get_dict())
			#print(response.text)		

	@task(2)
	def dashboard(self):
		self.client.verify = False
		logging.info('[%s] Return to dashboard====================',self.current_user)
		with self.client.get('/home', headers={'accept':'application/json, text/plain, */*','content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}, catch_response=True, name='dashboard', verify=False) as response:
			logging.debug(response.status_code)
			logging.debug(response.cookies)
			#logging.debug("[Dict] +++++++++++++++++++++++++")
			#logging.debug(self.client.cookies.get_dict())
			#print(response.text)

		with self.client.get('/public/__ENV.js', catch_response=True, name='dashboard', verify=False) as response:
			logging.debug(response.status_code)

		with self.client.get('/runtime.514b8778286f2bd8.esm.js', catch_response=True, name='dashboard', verify=False ) as response:
			logging.debug(response.status_code)

		with self.client.get('/polyfills.0aab7110e6d8af96.esm.js', catch_response=True, name='dashboard', verify=False ) as response:
			logging.debug(response.status_code)

		with self.client.get('/main.9810e95c3855dcfe.esm.js', catch_response=True, name='dashboard', verify=False ) as response:
			logging.debug(response.status_code)

		with self.client.get('/sgds-icons.0dc42d75a6d05f595921.ttf', catch_response=True, name='dashboard', verify=False ) as response:
			logging.debug(response.status_code)

		with self.client.get('/d36bd175268f5fd4.woff', catch_response=True, name='dashboard', verify=False ) as response:
			logging.debug(response.status_code)

		with self.client.get('/beta-character.481cd27.svg', catch_response=True, name='dashboard', verify=False ) as response:
			logging.debug(response.status_code)

		#5 call activities
		with self.client.get('/core/transaction/activities?sortBy=createdAt&asc=false&page=1&limit=3', headers={'accept':'application/json, text/plain, */*','content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}, catch_response=True, name='dashboard', verify=False ) as response:
			logging.debug(response.status_code)
			logging.debug(response.text)	

		#6 call files
		with self.client.get('/core/file/all-files?sortBy=lastViewedAt&asc=false&page=1&limit=5&statuses=active,expired,revoked&ignoreNull=true', headers={'accept':'application/json, text/plain, */*','content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}, catch_response=True, name='dashboard', verify=False ) as response:
			logging.debug(response.status_code)
			logging.debug(response.text)	

		with self.client.get('/ica-logo-only.10b42bf.svg', catch_response=True, name='dashboard', verify=False ) as response:
			logging.debug(response.status_code)	

	@task(1)
	def all_activities(self):
		self.client.verify = False
		logging.info('[%s] LHS All Activities====================',self.current_user)
		with self.client.get('/core/transaction/activities?sortBy=createdAt&asc=false&page=1&limit=10', headers={'accept':'application/json, text/plain, */*','content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}, catch_response=True, name='LHS-menu-all-activities', verify=False ) as response:
			logging.debug(response.status_code)
			logging.debug(response.cookies)
			#logging.debug("[Dict] +++++++++++++++++++++++++")
			#logging.debug(self.client.cookies.get_dict())
			#print(response.text)

	#@task(2)
	#def go_community(self):
	#	print('ProcessNumberTask|go_community------------------------')
		#self.client.get('/community', verify=False)
	#	self.client.get('/', verify=False)

	#@task(3)
	#def go_career(self):
	#	print('ProcessNumberTask|go_career------------------------')
		#self.client.get('/careers', verify=False)
	#	self.client.get('/', verify=False)				

class Userflow(TaskSet):
	def on_start(self):
		#self.client.verify = False
		self.client.get('/', verify=False)
				
	@task(1)
	def check_flow(self):
		self.client.get('/', verify=False)
		#step 1
		#self.client.get('/about/about-us', verify=False)
		#step 2
		#self.client.get('/workplace', verify=False)
		#step 3
		#self.client.get('/partners', verify=False)

class HelloWorldUser(HttpUser):
    wait_time = between(0.5, 2.5)
    def on_start(self):
    	logging.info('Initial Startup for each vu========================')

    tasks = [PortalAccess]

    def __init__(self, environment):
        super(HelloWorldUser, self).__init__(environment)
        global ACCOUNTS
        if (ACCOUNTS == None):
            with open('test.csv') as f:
                reader = csv.reader(f)
                ACCOUNTS = list(reader)


class StagesShape(LoadTestShape):
	"""
	A simply load test shape class that has different user and spawn_rate at
	different stages.
	Keyword arguments:
	stages -- A list of dicts, each representing a stage with the following keys:
	duration -- When this many seconds pass the test is advanced to the next stage
	users -- Total user count
	spawn_rate -- Number of users to start/stop per second
	stop -- A boolean that can stop that test at a specific stage
	stop_at_end -- Can be set to stop once all stages have run.
	The load will start with 0 users and ramp up to 10 users with a spawn rate of 10 until the 5 seconds mark
	"""

	stages = [
		{"duration": 30, "users": 7, "spawn_rate": 1},
		#{"duration": 60, "users": 100, "spawn_rate": 10},
		#{"duration": 120, "users": 200, "spawn_rate": 10},
		#{"duration": 180, "users": 300, "spawn_rate": 10},
		#{"duration": 240, "users": 400, "spawn_rate": 10},
		{"duration": 60, "users": 3, "spawn_rate": 1},
		{"duration": 90, "users": 1, "spawn_rate": 1}
	]

	def tick(self):
		run_time = self.get_run_time()

		for stage in self.stages:
			if run_time < stage["duration"]:
				tick_data = (stage["users"], stage["spawn_rate"])
				return tick_data

		return None