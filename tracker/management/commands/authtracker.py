from django.core.management.base import BaseCommand
from tracker.models import TrackerAccount, TrackerSetting
from tracker.services.tracker_service import default_auth

from django.db import transaction

from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    help = 'Auth for tracker account'

    def handle(self, *args, **options):
        user_id = input('user_id: ')

        try:
            tracker_account = TrackerAccount.objects.get(telegram_id=user_id)
            tracker_setting = TrackerSetting.objects.get(tracker_account_id=tracker_account.id)

            api_id = tracker_account.api_id
            api_hash = tracker_account.api_hash

            self.stdout.write(self.style.SUCCESS('auth...'))

            session_string = default_auth(api_id, api_hash)

            if session_string:

                tracker_setting.session_string = session_string

                tracker_setting.save()

                self.stdout.write(self.style.SUCCESS('Success'))
                self.stdout.write(f'Saved to {user_id}')
            else:
                self.stdout.write(self.style.ERROR('Failed'))

        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR('No such user'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Auth error {e}'))
