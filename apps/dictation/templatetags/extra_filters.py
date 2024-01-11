"""Extra filters."""
from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter(name="starize")
def starize(level):
    return "⭐" * int(level)


@register.filter(name="duration")
def get_duration(dictation):
    a = dictation.timestamps["data"][0]
    b = dictation.timestamps["data"][-1]
    return round(b / 60 - a / 60)


@register.simple_tag(name="practice_status")
def practice_status(is_done, user_current_line, total_line, lines):
    """Return the progress status for a given dictation.

    In order to have 2 arguments: @register.simple_tag
    https://docs.djangoproject.com/en/5.0/howto/custom-template-tags/#simple-tags


    If you click on the right arrow to the last sentence and then answer it (as your first answer),
    the progress bar will display 100% which is because the calcul is just from user_current_line.
    If each answer is recorded in list, it's possible to count the lenght of that list of answered
    to make the avaerage based on the number of answer, no matter the user_current_line.
    So we have to save that list intead of a simple integer. the user_current_line will be the last entry.
    """
    percent_progress = (
        round((len(lines["data"]) / total_line) * 100) if len(lines["data"]) > 0 else 0
    )
    if user_current_line == 0 or not user_current_line:
        status = mark_safe('<i class="fa-solid fa-eye"></i>')
    elif is_done:
        status = mark_safe('<i class="fa-solid fa-check text-success"></i>')
    else:
        status = mark_safe(
            '<div class="progress" role="progressbar" aria-label="Basic example" '
            + 'aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">'
            + f'<div class="progress-bar" style="width: {percent_progress}%">{percent_progress}%</div></div>'
        )

    return status
