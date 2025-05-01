from django.db import models

from core.model_mixins import CreatedUpdatedMixin, StartEndDateMixin
from core.models import Organization
from core.utils import timedelta_to_time
from layouts.models import Activity


class Supervision(CreatedUpdatedMixin, StartEndDateMixin):
    name = models.CharField(max_length=255, null=True)
    worker = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='worker_supervisions')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='organization_supervisions')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='user_supervisions')
    valid = models.BooleanField(default=True)

    def __str__(self):
        return self.name or f'Supervision {self.id}'


class ActivityStatistics(CreatedUpdatedMixin, StartEndDateMixin):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='statistics')
    supervision = models.ForeignKey(Supervision, on_delete=models.CASCADE, related_name='statistics')

    def __str__(self):
        return f"Statistics for {self.activity.name}"

    @property
    def delta(self):
        if self.end_date and self.start_date:
            return timedelta_to_time(self.end_date - self.start_date)


class Comment(CreatedUpdatedMixin):
    text = models.TextField()
    supervision = models.ForeignKey(Supervision, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f"Comment {self.id}"


class CommentImage(CreatedUpdatedMixin):
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return f"Image {self.id}"
