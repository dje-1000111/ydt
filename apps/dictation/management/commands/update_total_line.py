from django.core.management.base import BaseCommand
from django.core import management

from apps.dictation.models import Dictation


class Command(BaseCommand):
    """Command class.

    In order to avoid this calculation on each page loading (on the fly) which
    can be intensive in bandwidth and/or resources if the number of files is large.

    The number of lines is used to calculate the user's progress rate for a dictation.
    Depending on how the text file was prepared, the number of line breaks may vary over
    time if we make changes.

    It is therefore necessary to make an update for each modification within a text file
    or for each addition of a new text file.

    This calculation allows you to display all the progress of each dictation for a
    user on the table on the home page.
    """

    def update_total_line(self):
        """Update the total_line field."""
        dictation = Dictation()
        filenames = [dictation.filename for dictation in Dictation.objects.all()]
        for filename in filenames:
            Dictation.objects.filter(filename=filename).update(
                total_line=dictation.total_lines(filename)
            )

    def handle(self, *args, **kwargs):
        """Handle the update of the total_line field."""
        management.call_command("migrate", verbosity=0, interactive=False)

        self.update_total_line()
        self.stdout.write(self.style.SUCCESS("The total_line field has been filled."))
