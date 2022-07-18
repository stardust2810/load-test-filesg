from locust import HttpUser, task, between, TaskSet

class ProcessNumberTask(TaskSet):
	def on_start(self):
		self.client.verify = False

	@task(1)
	def go_ha(self):
		self.client.get('/health-ambassadors', verify=False)

	@task(2)
	def go_community(self):
		self.client.get('/community', verify=False)

	@task(3)
	def go_career(self):
		self.client.get('/careers', verify=False)				

class Userflow(TaskSet):
	def on_start(self):
		self.client.verify = False
				
	@task(1)
	def check_flow(self):
		#step 1
		self.client.get('/about/about-us', verify=False)
		#step 2
		self.client.get('/workplace', verify=False)
		#step 3
		self.client.get('/partners', verify=False)

class HelloWorldUser(HttpUser):
    wait_time = between(0.5, 2.5)
    tasks = [ProcessNumberTask, Userflow]

    @task
    def hello_world(self):
        self.client.get('/', verify=False)