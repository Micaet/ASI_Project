from locust import HttpUser, between, task


class SpaceMonitorUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_iss_current(self):
        self.client.get("/iss/current")

    @task(2)
    def get_iss_history(self):
        self.client.get("/iss/history?limit=50")

    @task(2)
    def get_launches_upcoming(self):
        self.client.get("/launches/upcoming")

    @task(1)
    def get_launches_past(self):
        self.client.get("/launches/past")

    @task(1)
    def get_health(self):
        self.client.get("/health")
