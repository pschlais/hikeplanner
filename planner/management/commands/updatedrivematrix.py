from django.core.management.base import BaseCommand
from planner.PlannerUtils import updateTable

class Command(BaseCommand):
    help = ('Updates trailhead-major city combinations in the ' +
            'DriveTimeMajorCity table/intermediate model.')

    def add_arguments(self, parser):
        # Named (optional arguments)
        parser.add_argument(
            '--newonly',
            action='store_true',
            dest='new_only',
            help=('Only query Google Distance Matrix API for new table ' +
                  'entries (default)'),
        )

        parser.add_argument(
            '--erroronly',
            action='store_true',
            dest='error_only',
            help=('Only query Google Distance Matrix API for table entries ' +
                  'with error code'),
        )

        parser.add_argument(
            '--all',
            action='store_true',
            dest='allentries',
            help=('Query Google Distance Matrix API for new & error table ' +
                  'entries'),
        )

    def handle(self, *args, **options):
        # update drive time matrix table entries
        if options['error_only']:
            output = updateTable.updateDriveTimeEntries(run_new=False,
                                                        run_errors=True)
        elif options['allentries']:
            output = updateTable.updateDriveTimeEntries(run_new=True,
                                                        run_errors=True)
        else:
            # default (run new, omit errors)
            output = updateTable.updateDriveTimeEntries()

        # print output
        for s in output['print_output']:
            self.stdout.write(s)
