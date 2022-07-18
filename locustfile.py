from locust import HttpUser, task, between, TaskSet

class ProcessNumberTask(TaskSet):
	@task(1)
	def go_ha(self):
		self.client.get('/health-ambassadors')

	@task(2)
	def go_community(self):
		self.client.get('/community')

	@task(3)
	def go_career(self):
		self.client.get('/careers')				

class Userflow(TaskSet):
	@task(1)
	def check_flow(self):
		#step 1
		self.client.get('/about/about-us')
		#step 2
		self.client.get('/workplace')
		#step 3
		self.client.get('/partners')

class HelloWorldUser(HttpUser):
    wait_time = between(0.5, 2.5)
    tasks = [ProcessNumberTask, Userflow]

    @task
    def hello_world(self):
        self.client.get('/')