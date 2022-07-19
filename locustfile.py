from locust import HttpUser, task, between, TaskSet
import json, string, secrets

class ProcessNumberTask(TaskSet):
	global filesg

	def on_start(self):
		request_body = {'authCode':'S3002610A','nonce':'mock'}
		self.client.verify = False
		with self.client.post('/core/auth/mock-login', json=request_body, headers={'accept':'application/json, text/plain, */*','content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}, catch_response=True ) as response_token:
			print(response_token.status_code)
			print(response_token.cookies)
			filesg = response_token.cookies.get('filesg-cookie-id')
			csrf = response_token.cookies.get('filesg-csrf-id')
			print("[Dict] +++++++++++++++++++++++++")
			print(self.client.cookies.get_dict())
			print(filesg)
			print(csrf)
			print(response_token.cookies['filesg-csrf-id'])
			#self.client.cookies.set('filesg-cookie-id', filesg)
			
		print("+++++++++++++++++++++++++")
		self.client.cookies = response_token.cookies
		csrf_token = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		#self.client.cookies['filesg-csrf-id'] = csrf_token
		self.client.cookies.set('filesg-csrf-id', csrf_token)
		#self.client.cookies.set_cookie('filesg-csrf-id', csrf_token)

		print(self.client.cookies.get('filesg-cookie-id'))
		print(self.client.cookies.get('filesg-csrf-id'))
		
		cookie='filesg-cookie-id='+self.client.cookies.get('filesg-cookie-id')+'; filesg-csrf-id='+csrf_token
		self.clients.headers.update({'cookie', cookie})
		print("+++++++++++++++++++++++++")

	@task(1)
	def go_ha(self):
		#self.client.get('/health-ambassadors', verify=False)
		#self.client.get('/', verify=False)
		# set cookie for request
		#self.client.cookies.set('filesg-cookie-id', filesg)
		cookie='filesg-cookie-id='+self.client.cookies.get('filesg-cookie-id')+'; filesg-csrf-id='+self.client.cookies.get('filesg-csrf-id')
		print(">>>>>>>>>>>>>>>>>>>>>>>>>")
		print(self.client.cookies.get('filesg-cookie-id'))
		print(self.client.cookies.get('filesg-csrf-id'))
		print(">>>>>>>>>>>>>>>>>>>>>>>>>")
		#with self.client.post('/auth/user-session-details', cookies=self.client.cookies.get_dict(), headers={'accept':'application/json, text/plain, */*','cookie':cookie, 'content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}, catch_response=True ) as response_token:
		with self.client.post('/transaction/activities?sortBy=createdAt&asc=true', cookies={'filesg-cookie-id':self.client.cookies.get('filesg-cookie-id'),'filesg-csrf-id':self.client.cookies.get('filesg-csrf-id')}, headers={'accept':'application/json, text/plain, */*','cookie':cookie, 'content-type':'application/json', 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}, catch_response=True ) as response_token:
			print("========================")
			print(response_token.status_code)
			print(response_token.text)
			print(response_token.cookies.get('filesg-cookie-id'))
			print(response_token.cookies.get('filesg-csrf-id'))
			print("========================")

			json_var = response_token.json()
			name=json_var['name']
			print('*************Name = ' + name)

	@task(2)
	def go_community(self):
		#self.client.get('/community', verify=False)
		self.client.get('/', verify=False)

	@task(3)
	def go_career(self):
		#self.client.get('/careers', verify=False)
		self.client.get('/', verify=False)				

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
    tasks = [ProcessNumberTask]

    #@task
    #def hello_world(self):
    #    self.client.get('/', verify=False)
    #    print(self.client.cookies.get('filesg-cookie-id'))
    #    print(self.client.cookies.get('filesg-csrf-id'))