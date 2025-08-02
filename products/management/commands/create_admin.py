from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Create a hardcoded admin user with username "admin" and password "admin"'

    def handle(self, *args, **options):
        # Check if admin user already exists
        if User.objects.filter(username='admin').exists():
            # Update existing admin user
            admin_user = User.objects.get(username='admin')
            admin_user.password = make_password('admin')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS('Admin user updated successfully!')
            )
        else:
            # Create new admin user
            User.objects.create_user(
                username='admin',
                email='admin@fusiontec.com',
                password='admin',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(
                self.style.SUCCESS('Admin user created successfully!')
            )
        
        self.stdout.write(
            self.style.WARNING('Username: admin')
        )
        self.stdout.write(
            self.style.WARNING('Password: admin')
        ) 