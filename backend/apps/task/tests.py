from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.project.models import Project
from apps.task.models import Column
from apps.users.models import User


class TaskApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@test.com",
            password="password123",
            role="member",
        )
        self.reader = User.objects.create_user(
            username="reader",
            email="reader@test.com",
            password="password123",
            role="reader",
        )

        self.project = Project.objects.create(
            name="Projet A",
            description="",
            owner=self.owner,
            start_date=timezone.now(),
        )
        self.project.members.add(self.owner, self.reader)

        self.todo = Column.objects.create(project=self.project, name="A faire", order=0)

        self.other_project = Project.objects.create(
            name="Projet B",
            description="",
            owner=self.owner,
            start_date=timezone.now(),
        )
        self.other_project.members.add(self.owner)
        self.other_column = Column.objects.create(
            project=self.other_project, name="Terminé", order=0
        )

    def test_task_creation_rejects_column_from_another_project(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            reverse("task-list"),
            {
                "title": "Bug critique",
                "project": self.project.id,
                "column": self.other_column.id,
                "priority": "high",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("column", response.data)

    def test_reader_cannot_create_column(self):
        self.client.force_authenticate(self.reader)

        response = self.client.post(
            reverse("column-list"),
            {
                "project": self.project.id,
                "name": "Review",
                "order": 1,
                "color": "#2563eb",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
