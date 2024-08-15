from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Reduces the number of users in the database to 1000'

    def handle(self, *args, **options):
        max_users = 1000
        with transaction.atomic():
            current_user_count = User.objects.count()
            self.stdout.write(f"Current user count: {current_user_count}")

            if current_user_count > max_users:
                # Calculate how many users to delete
                users_to_delete_count = current_user_count - max_users
                self.stdout.write(f"Need to delete {users_to_delete_count} users.")

                # Fetch IDs of users to delete (e.g., the most recent ones)
                user_ids_to_delete = User.objects.all().order_by('-date_joined').values_list('id', flat=True)[:users_to_delete_count]

                # Use the list of IDs to form a new queryset and delete the users
                users_to_delete = User.objects.filter(id__in=list(user_ids_to_delete))
                deleted_count = users_to_delete.count()
                users_to_delete.delete()

                self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} users. New user count is {User.objects.count()}'))
            else:
                self.stdout.write(self.style.SUCCESS('No need to delete any users.'))
