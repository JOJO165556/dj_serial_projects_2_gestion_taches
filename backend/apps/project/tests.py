from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.project.models import Project
from apps.task.models import Column
from apps.users.models import User


class ProjectApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="owner",
            email="owner@test.com",
            password="password123",
            role="member",
        )
        self.client.force_authenticate(self.user)

    def test_create_project_initializes_owner_membership_and_default_columns(self):
        response = self.client.post(
            reverse("project-list"),
            {"name": "Projet produit", "description": "Board principal"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project = Project.objects.get(id=response.data["id"])

        self.assertEqual(project.owner, self.user)
        self.assertTrue(project.members.filter(id=self.user.id).exists())
        self.assertEqual(
            list(Column.objects.filter(project=project).values_list("name", flat=True)),
            ["A faire", "En cours", "Terminé"],
        )
