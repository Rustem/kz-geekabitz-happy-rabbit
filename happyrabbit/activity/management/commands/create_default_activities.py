from django.core.management import BaseCommand

from happyrabbit.activity.models import Category, ActivityModel as Activity


class Command(BaseCommand):
    help = 'Create default category and activities'

    def handle(self, *args, **options):

        category = Category(title='default', description='Default category for first start')
        category.save()

        activity = Activity(title='default', description='Default activity for first start', category=category)
        activity.save()
        activity = Activity(title='default2', description='Default activity 2 for first start', category=category)
        activity.save()

        self.stdout.write(self.style.SUCCESS('Successfully created default category and activity'))