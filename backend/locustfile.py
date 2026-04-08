"""Locust performance testing script for the OliveCapstone backend.

This module defines the load testing tasks and user behavior for simulating
concurrent users interacting with the foodshare API.
"""

import io
import random

from locust import HttpUser, between, task
from PIL import Image


class FoodshareUser(HttpUser):
    """Simulates a user of the BlackBearFoodShare application.

    Each user session starts by loading a valid authentication token and
    preparing a placeholder image for uploads.
    """

    wait_time = between(0.1, 0.5)  # More aggressive for stress testing

    tokens = []

    def on_start(self):
        """Initializes the user session with authentication and assets.

        Loads tokens from 'test_tokens.txt' on the first run and prepares
        a sample image for upload tasks.
        """
        # Load tokens once for the class
        if not FoodshareUser.tokens:
            try:
                with open("test_tokens.txt") as f:
                    FoodshareUser.tokens = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                print("Error: test_tokens.txt not found. Run seed_db.py first.")
                return

        # Assign a random token to this user session
        if FoodshareUser.tokens:
            self.token = random.choice(FoodshareUser.tokens)
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}

        # Generate a valid 100x100 white PNG image
        img = Image.new("RGB", (100, 100), color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        self.image_content = buf.getvalue()

    @task(50)
    def get_foodshares(self):
        """Simulate users viewing the foodshare list."""
        self.client.get("/foodshares", headers=self.headers)

    @task(1)
    def create_foodshare(self):
        """Simulate users uploading a new foodshare."""
        data = {
            "name": f"Stress Test Item {random.randint(1, 10000)}",
            "location": f"Building {random.randint(1, 50)}",
            "ends": "2026-12-31T23:59:59",
            "picture_expires": "2026-12-31T23:59:59",
            "active": "true",
        }
        # Use (filename, content, content_type) format for multipart uploads
        files = {"picture": ("stress.png", self.image_content, "image/png")}
        self.client.post("/foodshares", data=data, files=files, headers=self.headers)

    @task(1)
    def submit_survey(self):
        """Simulate users submitting feedback."""
        payload = {
            "num_participants": random.randint(1, 20),
            "experience": random.randint(1, 5),
            "other_thoughts": "Performance test survey submission.",
            "foodshare_fk_id": random.randint(1, 20),
        }
        self.client.post("/surveys", json=payload, headers=self.headers)
