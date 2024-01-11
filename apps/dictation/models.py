"""Models."""
import re
import base64
import math
from typing import Any
import requests
import json

from django.db import models
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model

from config import settings


class Dictation(models.Model):
    """Dictation model."""

    video_id = models.CharField(null=True, blank=True, max_length=50)
    filename = models.CharField(null=True, blank=True, max_length=200)
    timestamps = models.JSONField()
    topic = models.CharField(max_length=200)
    level = models.IntegerField()
    tip = models.JSONField()
    slug = models.SlugField(default="", null=False)
    total_line = models.IntegerField(default=0)
    in_production = models.BooleanField(default=False)

    def __str__(self):
        """Return str representation."""
        return self.topic

    def total_lines(self, filename: str = None) -> int:
        """Return the total number of lines."""
        filename = filename if filename else self.filename
        with open(settings.TXT_DIR / filename, "r", encoding="utf-8") as f:
            return len(f.readlines()) - 1

    def read_segment(self, filename: str, index: int, max_lines: int) -> str:
        """Return the line at the given index."""
        line = ""
        with open(f"{settings.TXT_DIR / filename}", "r", encoding="utf-8") as f:
            if index - 1 <= max_lines:
                line += f.readlines()[index - 1]
        return line

    def get_video_title(self, video_id: str) -> Any:
        """Get the original video title from YouTube."""
        payload = {
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "format": "json",
        }
        response = requests.get("https://www.youtube.com/oembed", payload, timeout=3)
        data = response.json()
        return data["title"]

    def get_filename(self, slug: str) -> Any:
        """Return the filename of the current dictation from the given slug."""
        dictation = Dictation.objects.filter(slug=slug).first()
        return dictation.filename

    def get_duration(self, dictation) -> int:
        """Return the duration (mn) of the given dictation."""
        first = dictation.timestamps["data"][0]
        last = dictation.timestamps["data"][-1]
        return round(last / 60 - first / 60)

    def thumbail_to_b64(self, video_id: str) -> str:
        """Return base64 image decoded."""
        img_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
        response = requests.get(img_url, timeout=3)
        b64 = base64.b64encode(response.content)
        return b64.decode("utf-8")


def lines_default():
    """Allow the default state of the field."""
    return {"data": []}


class Practice(models.Model):
    """Practice model class.

    We can rate the level,
    find out if you have already done the exercise,
    and save your progress to resume at the same level next time.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    dictation = models.ForeignKey(Dictation, on_delete=models.CASCADE)
    user_current_line = models.IntegerField(null=True, blank=True)
    lines = models.JSONField(default=lines_default)
    user_rating = models.CharField(null=True, blank=True, max_length=1)
    is_done = models.BooleanField("is_dictation_done", default=False)

    def __str__(self):
        """Return str representation."""
        return f"{self.dictation_id}"

    def average_rating(self) -> dict:
        """Calculate the average rating."""
        ratings = {}
        dictation_ids = list(set([i["id"] for i in Dictation.objects.values("id")]))
        for pk in dictation_ids:
            queryset = Practice.objects.values("user_rating").filter(dictation_id=pk)
            queratings = [int(i["user_rating"]) for i in queryset if i["user_rating"]]

            if queratings and len(queratings) > 0:
                ratings.update(
                    {f"dictation_{pk}": math.floor(sum(queratings) / len(queratings))}
                )
        return ratings

    def update_dictation_rating(self, ratings: dict):
        """Update the rating of each dictation."""
        for dictation, rating in ratings.items():
            level = Dictation.objects.filter(pk=dictation[10:]).update(level=rating)
        return level

    def create_dictation(self, user, dictation):
        """Initiate a new instance between a dictation and the user."""
        if not Practice.objects.filter(user=user, dictation=dictation).exists():
            Practice.objects.create(user=user, dictation=dictation)

    def save_dication_progress(self, user, dictation_id, current_line):
        """Save the number of the last line wherre the user stopped."""
        if Practice.objects.filter(user=user, dictation=dictation_id).exists():
            Practice.objects.filter(user=user, dictation=dictation_id).update(
                user_current_line=current_line
            )

    def update_answered_lines(self, practice, line_nb, new_page):
        """Update the list of good answers."""
        if line_nb - 1 not in practice.lines["data"] and new_page:
            practice.lines["data"].append(line_nb - 1)
            practice.save()
        return practice.lines["data"]

    def update_is_done(self, user, dictation_id):
        """Update the boolean is_done."""
        practice = (
            Practice.objects.filter(user=user, dictation_id=dictation_id)
            .select_related("dictation")
            .first()
        )
        total_line = practice.dictation.total_line
        if len(practice.lines["data"]) == total_line:
            Practice.objects.filter(user=user, dictation_id=dictation_id).update(
                is_done=True
            )

    def saved_position(self, user, dictation_id):
        """Return the last number of line in order to initiate the video at that point."""
        practice = Practice.objects.filter(user=user, dictation=dictation_id)
        return (
            practice.first().user_current_line
            if practice.first().user_current_line
            else 0
        )

    def get_lines(self, user, dictation):
        """Return the lines list."""
        return (
            Practice.objects.filter(user=user, dictation=dictation)
            .first()
            .lines["data"]
        )

    def get_rating(self, user, dictation_id):
        """Get the Practice instance."""
        return Practice.objects.filter(user=user, dictation_id=dictation_id).first()

    def update_rating(self, user, dictation_id, new_rating):
        """Update the rating number given by the click on the star."""
        Practice.objects.filter(user=user, dictation=dictation_id).update(
            user_rating=new_rating
        )


def contraction(segment: str) -> str:
    """Return converted contraction."""
    irregular = ["bleed", "breed", "feed", "shed", "speed"]
    segment_list = segment.split()
    for i in range(len(segment_list)):
        if segment_list[i + 1][-2:] != "ed" and segment_list[i + 1] not in irregular:
            segment = segment.replace("'d", " would")
        segment = segment.replace("'d", " had")

    if "'s" in segment:
        for word in segment_list:
            if "let" in word:
                segment = segment.replace("'s", " us")
            segment = segment.replace("'s", " is")

    if "n't" in segment:
        segment = segment.replace("n't", " not")

    if "'ll" in segment:
        segment = segment.replace("'ll", " will")

    if "'re" in segment:
        segment = segment.replace("'re", " are")

    if "'ve" in segment:
        segment = segment.replace("'ve", " have")

    return segment


class Historic:
    """Historic class."""

    def __init__(self):
        self.line_numbers = [-1]
        self.indexes = [-1]

    def re_init(self, line_number: int) -> Any:
        """Empty the lists when the line number change.

        Except for the first previous.
        There is a trick to get more than 3 reveal letters:
        you click on the right arrow (the forced next), then you click reveal once.
        And then you click on the left arrow so you have 3 new helps...
        But it's not a competition and there is no advantage to do that.
        The pure goal is to improve your listenning, comprehension, vocabulary, etc...
        """
        if self.line_numbers[-1] < line_number:
            self.indexes = []
        if self.line_numbers[-1] > line_number:
            line_number = self.line_numbers[:-1]
            self.indexes = []
        return self.indexes

    def tmp(self):
        """Tmp."""


historic = Historic()


def reveal_first_wrong_letter(
    segment,
    original_segment,
    line_number: int,
    reveal_status: bool,
) -> tuple[str, int]:
    """Return the wrong segment with the first wrong letter replaced by the correct one.

    The rest is potentially finished with stars.
    31 = len("<span class='spelling'>* or [a-z]</span>")
    """
    historic.re_init(line_number)

    spelling = "<span class='spelling'>"
    star = "*"

    original_segment = remove_punctuation(original_segment)
    original_segment = " ".join(original_segment)
    if spelling in segment or star in segment:
        if spelling in segment:
            index = segment.index(spelling)
        elif star in segment:
            index = segment.index(star)

        if line_number > max(set(historic.line_numbers)):
            historic.line_numbers.append(line_number)
            historic.indexes = []

        revealed_segment = (
            segment.replace(segment[index : 31 + index], original_segment[index], 1)
            if len(historic.indexes) < 3 and reveal_status
            else segment
        )

        if len(set(historic.indexes)) < 3 and index not in historic.indexes:
            historic.indexes.append(index)
    else:
        revealed_segment = segment

    attempts = len(set(historic.indexes))
    return revealed_segment, attempts


def correction(original_segment, new_segment, new_page: bool) -> tuple[str, bool, int]:
    """Return the corrected segment.

    The complete segment if is the same as the original.
    The first right part(s) eventually appened with stars of lenght
    of the missing words.
    """
    # original_without_contraction = contraction(original_segment)
    # owc = remove_punctuation(original_without_contraction)

    new_segment = remove_punctuation(new_segment)
    original_segment = remove_punctuation(original_segment)

    len_original_segment, len_new_segment = len(original_segment), len(new_segment)
    if len_new_segment < len_original_segment:
        new_segment += [""] * (len_original_segment - len_new_segment)
    if len_new_segment > len_original_segment:
        new_segment = new_segment[:len_original_segment]
    tmp: list = []
    corrected = []
    for index in range(len_original_segment):
        if original_segment[index] != new_segment[index]:
            correct_word = corrected_word(original_segment[index], new_segment[index])
            tmp.insert(index, correct_word)
        else:
            tmp.insert(index, new_segment[index])
    for index in range(len_original_segment):
        if "</span>" in tmp[index]:
            corrected = tmp[: index + 1]
            break
        corrected = tmp

    if corrected and len(corrected) < len_original_segment:
        for _ in range(len_original_segment - len(corrected)):
            corrected.append("*" * len(original_segment[len(corrected)]))

    len_indexes = len(historic.indexes) if not -1 in historic.indexes else 0
    if new_page:
        historic.indexes = []

    return " ".join(corrected), corrected == original_segment, len_indexes


def corrected_word(reference_word: str, new_word: str) -> str:
    """Return the corrected word.

    The right word,
    or the word hilighted with an underscore if there is a few mistakes otherwise full
    of stars and underscored.
    """
    correct_word = ""
    if len(new_word) > len(reference_word):
        reference_word += "_" * (len(new_word) - len(reference_word))
        new_word = new_word[: len(reference_word)]
    for index, letter in enumerate(new_word):
        if letter == reference_word[index]:
            correct_word += letter
        else:
            letter = f"<span class='spelling'>{letter}</span>"
            correct_word += mark_safe(letter)
    if len(correct_word) < len(reference_word):
        last_underscore = len(reference_word) - len(correct_word)
        star = "<span class='spelling'>*</span>"
        correct_word += mark_safe(star) * last_underscore
    return correct_word


def sanitize_longer(segment) -> str:
    """Return a string of maximum 26 chars."""
    segment = segment.split()
    for k, v in enumerate(segment):
        if len(v) > 26:
            segment[k] = v[:26]
    return " ".join(segment)


def remove_punctuation(segment: str) -> list:
    """Remove ponctuation specified in list.

    Allow the users to avoid typing these (and limit the amount of mistakes).
    """
    segment = sanitize_longer(segment)
    segment = re.sub(r"\-(?=\w)|(?<=\w)\-", " ", segment)
    segment = segment.replace(" - ", " ")
    segment = "".join([i for i in segment if i not in settings.PONCTUATION])
    return segment.strip().split()


def get_word_definition(word):
    # breakpoint()
    if word and word.isalpha():
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        payload = {
            "format": "json",
        }
        response = requests.get(url, payload, timeout=3)
        data = response.json()
        if "title" in data:
            result = [data["title"]]
        else:
            result = [
                v[0]["definitions"]
                for i in data
                for k, v in i.items()
                if k == "meanings"
            ][0]
            result = {k: i["definition"] for k, i in enumerate(result)}
        # result = ""
        # if "title" in data:
        #     result = data["title"]
        # else:
        #     result += data[0]["meanings"][0]["definitions"][0]["definition"]
    else:
        result = []
    return json.dumps(result)
