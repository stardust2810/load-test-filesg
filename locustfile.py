from locust import HttpUser, task, between, TaskSet, LoadTestShape, events, constant, SequentialTaskSet
import json, string, secrets, time, logging, sys, csv, requests, re, random
from lxml import html

#disable cert verification warnings
requests.packages.urllib3.disable_warnings() 
ACCOUNTS = None

#-------------------------------------------
# For getting embedded resources from a page
#
resource_paths = [
            '//link[@rel="stylesheet"]/@href',
            '//link[@rel="Stylesheet"]/@href',
            '//link[@rel="STYLESHEET"]/@href',
            '//link[@rel="preconnect"]/@href',
            '//link[@rel="icon"]/@href',
            '//link[@rel="apple-touch-icon"]/@href',
            "//script/@src",
            "//img/@src",
            "//source/@src",
            "//embed/@src",
            "//body/@background",
            '//input[@type="image"]/@src',
            '//input[@type="IMAGE"]/@src',
            '//input[@type="Image"]/@src',
            "//object/@data",
            "//frame/@src",
            "//iframe/@src",
        ]
#
#
def get_embedded_resources(response_content, filter='.*'):
    resources = []
    tree = html.fromstring(response_content)
    for resource_path in resource_paths:
        for resource in tree.xpath(resource_path):
            if re.search(filter, resource): resources.append(resource)
    return resources
#
#-------------------------------------------


class FileSGUserActivities(TaskSet):
	#currently logged in user
	current_user = 'NOT FOUND'
	nonce = 'NOT FOUND'

	#holds all the recent activities for the current user
	all_activities = None

	#holds all the files for an activity for the current user
	individual_activity_files = None

	#holds all the recent files for the current user
	all_files = None

	#user is able to login to their dashboard
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
		logging.info('[%s][Mock Login][Home page]',self.current_user)
		with self.client.post('/', headers={'accept':'application/json, text/plain, */*','content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36','cookie':'filesg-csrf-id='+csrf_token}, catch_response=True) as response:
			logging.debug(response.status_code)
			logging.debug(response.cookies)
			#logging.debug("[Dict] +++++++++++++++++++++++++")
			#logging.debug(self.client.cookies.get_dict())

		#2 call get user details to create a session, should return csrf, filesg_cookie
		logging.info('[%s][Mock Login][User session]',self.current_user)
		with self.client.get('/core/auth/user-session-details', headers={'authority':'www.dev.file.gov.sg','accept':'application/json, text/plain, */*','user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36','x-csrf-token':csrf_token,'cookie':'filesg-csrf-id='+csrf_token}, catch_response=True, name='get-session') as response:
			logging.debug(response.status_code)
			logging.debug(response.cookies)

		#3 call mock login with payload which returns filesg_cookie
		logging.info('[%s][Mock Login][Login]',self.current_user)
		request_body = {'authCode':self.current_user,'nonce':'mock'}
		with self.client.post('/core/auth/mock-login', json=request_body, headers={'accept':'application/json, text/plain, */*','content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}, catch_response=True, name='mock-login') as response:
			logging.debug(response.status_code)
			logging.debug(response.cookies)

		#5 call activities
		logging.info('[%s][Mock Login][Activities]',self.current_user)
		with self.client.get('/core/transaction/activities?sortBy=createdAt&asc=false&page=1&limit=3', headers={'accept':'application/json, text/plain, */*','content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}, catch_response=True, name='dashboard/activities') as response:
			if(response.ok):
				self.all_activities = response.json()["items"]
				for each_activity in self.all_activities:
					logging.info('[%s][Activity][UUID] : %s', self.current_user, each_activity['uuid'])
					self.individual_activity_files = each_activity['files']
					for each_file in self.individual_activity_files:
						logging.info('[%s][Activity][File][UUID] : %s : %s', self.current_user, each_file['uuid'], each_file['name'])

				logging.info('[%s][Count of activities][%s]',self.current_user,len(self.all_activities))

		#6 call files
		logging.info('[%s][Mock Login][Files]',self.current_user)
		with self.client.get('/core/file/all-files?sortBy=lastViewedAt&asc=false&page=1&limit=5&statuses=active,expired,revoked&ignoreNull=true', headers={'accept':'application/json, text/plain, */*','content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}, catch_response=True, name='dashboard/files') as response:
			logging.debug(response.status_code)
			logging.debug(response.cookies)

			#TODO : Get the list of recently viewed files and store in self.all_files	

	#A user is able to return to the dashboard, which will load the latest 3 activities and files
	@task(2)
	def dashboard(self):
		logging.info('[%s][Back to dashboard]',self.current_user)
		with self.client.get('/home', headers={'accept':'application/json, text/plain, */*','content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}, catch_response=True, name='dashboard') as response:
			logging.debug(response.status_code)
			logging.debug(response.cookies)
			#logging.debug("[Dict] +++++++++++++++++++++++++")
			#logging.debug(self.client.cookies.get_dict())
			#print(response.text)
			resources = get_embedded_resources(response.content)
			for resource in resources:
				if re.search("^https?://", resource) == None: resource = self.client.base_url + "/" + resource
				#see consolidated or individual resources
				#self.client.get(resource, name="dashboard/resources")
				self.client.get(resource,  name='dashboard')

		#5 call activities
		with self.client.get('/core/transaction/activities?sortBy=createdAt&asc=false&page=1&limit=3', headers={'accept':'application/json, text/plain, */*','content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}, catch_response=True, name='dashboard') as response:
			#logging.info('[%s][Response]',response.status_code)
			if(response.ok):
				#logging.info(response.json())
				#for key, value in response.json().items():
					#logging.debug("Key is %s : Value is %s", key, value)
				self.all_activities = response.json()["items"]
				for each_activity in self.all_activities:
					#logging.info("JSON [Each Item in the list of JSON Objects] =======================================")
					#logging.info(each_item)
					logging.info('[%s][Activity][UUID] : %s', self.current_user, each_activity['uuid'])
					self.individual_activity_files = each_activity['files']
					for each_file in self.individual_activity_files:
						logging.info('[%s][Activity][File][UUID] : %s : %s', self.current_user, each_file['uuid'], each_file['name'])

			#if response.status_code == 200:
			#	logging.info("OK")
			#else:
			#	logging.warning("No info")

		#6 call files
		with self.client.get('/core/file/all-files?sortBy=lastViewedAt&asc=false&page=1&limit=5&statuses=active,expired,revoked&ignoreNull=true', headers={'accept':'application/json, text/plain, */*','content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}, catch_response=True, name='dashboard') as response:
			#logging.info('[%s][Response]',response.status_code)
			if(response.ok):
				#logging.info(response.json())
				#for key, value in response.json().items():
					#logging.debug("Key is %s : Value is %s", key, value)
				all_files = response.json()["items"]

				for each_file in all_files:
					#logging.info("JSON [Each Item in the list of JSON Objects] =======================================")
					#logging.info(each_item)
					logging.info('[%s][File][UUID] : %s : %s', self.current_user, each_file['uuid'], each_file['name'])						

		#misc resources ---------------------------------------------------
		#with self.client.get('/sgds-icons.0dc42d75a6d05f595921.ttf', catch_response=True, name='dashboard') as response:
		#	logging.debug(response.status_code)

		#with self.client.get('/d36bd175268f5fd4.woff', catch_response=True, name='dashboard') as response:
		#	logging.debug(response.status_code)

		#with self.client.get('/beta-character.481cd27.svg', catch_response=True, name='dashboard') as response:
		#	logging.debug(response.status_code)

		#with self.client.get('/ica-logo-only.10b42bf.svg', catch_response=True, name='dashboard', verify=False ) as response:
		#	logging.debug(response.status_code)	

	#from the LHS menu, go to the All Activities page
	@task
	def all_activities(self):
		logging.info('[%s][LHS][All Activities]', self.current_user)
		with self.client.get('/core/transaction/activities?sortBy=createdAt&asc=false&page=1&limit=10', headers={'accept':'application/json, text/plain, */*','content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}, catch_response=True, name='LHS-menu-all-activities') as response:
			logging.debug(response.status_code)
			logging.debug(response.cookies)

	#from dashboard, a user is able to view the individual activity
	@task(3)
	def view_individual_activity(self):
		logging.info('[%s][View Individual Activity]',self.current_user)
		
		#check if list is empty or not. If not empty, access a random activity
		if self.all_activities:
			#randomly select an activity to view
			activity_to_view = random.choice(self.all_activities)
			try:
				with self.client.get('/activities/'+activity_to_view['uuid'], headers={'accept':'application/json, text/plain, */*','content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}, catch_response=True, name='LHS-menu-all-activities') as response:
					response.raise_for_status()
					logging.info('[%s][View Individual Activity][%s]',self.current_user,activity_to_view['uuid'])
					#view the files within the activity
					
					##if status code within 200 - 400. Might not need with raise for status.
					#if response.ok:
					#	logging.info('[%s][View Activity][%s]',self.current_user,activity_to_view['uuid'])		
					#else:
					#	logging.warning("[%s][View Activity][Unable to retrieve individual activity",self.current_user)
			except HTTPError as http_err:
				logging.error(http_err)
			except Exception as err:
				logging.error(err)
		else:
			logging.info('[%s][View Individual Activity][No activities available]',self.current_user)			

	#from dashboard, a user is able to view the file(s)
	@task(3)
	def view_file(self):
		logging.info('[%s][View file]',self.current_user)
		#tbc		

	def on_stop():
		logging.info("[%s][Logging out]",self.current_user)

#TODO
class NonFileSGUserActivities(TaskSet):
	def on_start(self):
		self.client.get('/')
				
	@task(1)
	def check_flow(self):
		self.client.get('/')

class FileSGPerformanceTest(HttpUser):
    wait_time = between(0.5, 2.5)
    def on_start(self):
    	logging.info('[Main][On start for each vu]')

    tasks = [FileSGUserActivities]

    def __init__(self, environment):
        super(FileSGPerformanceTest, self).__init__(environment)
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
		{"duration": 160, "users": 2, "spawn_rate": 1},
		{"duration": 320, "users": 4, "spawn_rate": 1},
		{"duration": 480, "users": 7, "spawn_rate": 1},
		#{"duration": 60, "users": 100, "spawn_rate": 10},
		#{"duration": 120, "users": 200, "spawn_rate": 10},
		#{"duration": 180, "users": 300, "spawn_rate": 10},
		#{"duration": 240, "users": 400, "spawn_rate": 10},
		{"duration": 640, "users": 5, "spawn_rate": 1},
		{"duration": 800, "users": 3, "spawn_rate": 1},
		{"duration": 960, "users": 1, "spawn_rate": 1}
	]

	def tick(self):
		run_time = self.get_run_time()

		for stage in self.stages:
			if run_time < stage["duration"]:
				tick_data = (stage["users"], stage["spawn_rate"])
				return tick_data

		return None