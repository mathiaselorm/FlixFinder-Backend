from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from getpass import getpass
import json
from faker import Faker
import random

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Generate fake users for the CustomUser model'

    def add_arguments(self, parser):
        parser.add_argument('num_users', type=int, help='Number of fake users to create')

    @transaction.atomic
    def handle(self, *args, **options):
        num_users = options['num_users']
        self.stdout.write(f"Creating {num_users} fake users...")
        default_password = getpass("Enter the default password for all users: ")
        created_count = 0

        while created_count < num_users:
            email = fake.unique.email()  # Ensures email is unique within this run
            first_name = fake.first_name()
            last_name = fake.last_name()
            phone_number = fake.phone_number() if random.choice([True, False]) else None
            date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=70) if random.choice([True, False]) else None
            gender = random.choice(['male', 'female', 'other'])
            location = fake.address() if random.choice([True, False]) else ""
            bio = fake.text(max_nb_chars=200) if random.choice([True, False]) else ""
            preferences = json.dumps({'genres': random.sample(['Action', 'Comedy', 'Drama', 'Fantasy', 'Adventure', 'Animation', 'Documentary', 'Horror', 'Romance', 'Science Fiction (Sci-Fi)', 'War'], k=2)})

            try:
                user = User.objects.create_user(
                    email=email,
                    password=default_password,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    date_of_birth=date_of_birth,
                    gender=gender,
                    location=location,
                    bio=bio,
                    preferences=preferences,
                    is_active=random.choice([True, True, True, True, True, False])
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created user: {email}'))
                created_count += 1
            except IntegrityError as e:
                self.stdout.write(self.style.WARNING(f'Failed to create user with email {email}: {str(e)}'))
                fake.unique.clear()  # Reset the Faker unique instance to avoid infinite loops

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} fake users.'))
