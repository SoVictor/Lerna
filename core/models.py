from django.db    import models
from django.urls  import reverse
from django.utils import timezone
from users.models import User


class Problem(models.Model):
    name                 = models.CharField(max_length=80)
    path                 = models.CharField(max_length=255)
    author               = models.CharField(max_length=64, blank=True, db_index=True)
    developer            = models.CharField(max_length=64, blank=True, db_index=True)
    origin               = models.CharField(max_length=128, blank=True, db_index=True)
    description          = models.TextField()
    input_specification  = models.TextField(blank=True)
    output_specification = models.TextField(blank=True)
    samples              = models.TextField(blank=True)
    explanations         = models.TextField(blank=True)
    notes                = models.TextField(blank=True)
    input_file           = models.CharField(max_length=16, blank=True)
    output_file          = models.CharField(max_length=16, blank=True)
    time_limit           = models.PositiveIntegerField()
    memory_limit         = models.PositiveIntegerField()
    checker              = models.CharField(max_length=100)
    mask_in              = models.CharField(max_length=32)
    mask_out             = models.CharField(max_length=32, blank=True)
    analysis             = models.TextField(blank=True)
    created_at           = models.DateTimeField(auto_now_add=True)
    updated_at           = models.DateTimeField(auto_now=True)

    class Meta:
        db_table      = 'problems'
        get_latest_by = 'created_at'

    @property
    def time_limit_in_secs(self):
        if self.time_limit % 1000 == 0:
            return self.time_limit // 1000
        else:
            return self.time_limit / 1000

    @time_limit_in_secs.setter
    def time_limit_in_secs(self, value):
        self.time_limit = int(value * 1000 + .5)

    def __str__(self):
        return self.name


class ContestManager(models.Manager):
    def privileged(self, user):
        return self.get_queryset() if user.is_staff else self.filter(is_admin=False)


class Contest(models.Model):
    name          = models.CharField(max_length=255)
    description   = models.TextField(blank=True)
    start_time    = models.DateTimeField(blank=True, null=True)
    duration      = models.PositiveIntegerField(blank=True, null=True)
    freezing_time = models.IntegerField(blank=True, null=True)
    is_school     = models.BooleanField()
    is_admin      = models.BooleanField()
    is_training   = models.BooleanField()
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)
    problems      = models.ManyToManyField(Problem, through='ProblemInContest')

    objects = ContestManager()

    class Meta:
        db_table      = 'contests'
        get_latest_by = 'created_at'

    @property
    def problem_count(self):
        return self.problem_in_contest_set.count()

    @property
    def duration_str(self):
        return '%d:%02d' % divmod(self.duration, 60)

    def __str__(self):
        return self.name if len(self.name) <= 70 else self.name[:67] + '...'

    def get_absolute_url(self):
        # TODO: Replace with something more appropriate.
        return reverse('contests:problem', args=[self.id, 1])

    @classmethod
    def three_way_split(cls, contests, threshold_time):
        """
        Splits the given iterable into three lists: actual, awaiting and past contests,
        regarding the given time point.
        """

        actual = []
        awaiting = []
        past = []
        for contest in contests:
            if contest.start_time > threshold_time:
                awaiting.append(contest)
            elif contest.start_time + timezone.timedelta(minutes=contest.duration) < threshold_time:
                past.append(contest)
            else:
                actual.append(contest)
        return actual, awaiting, past


class PICManager(models.Manager):
    def is_visible(self, problem):
        return self.filter(problem=problem, contest__is_admin=False).exists()


class ProblemInContest(models.Model):
    problem    = models.ForeignKey(Problem)
    contest    = models.ForeignKey(Contest)
    number     = models.PositiveIntegerField()
    score      = models.IntegerField(blank=True, null=True)
    # TODO: Remove this field.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PICManager()

    class Meta:
        db_table             = 'problem_in_contests'
        default_related_name = 'problem_in_contest_set'
        verbose_name_plural  = 'problems in contest'
        get_latest_by        = 'created_at'

    def __str__(self):
        return '{0.contest.id:03}#{0.number}: "{0.problem}"'.format(self)

    def get_absolute_url(self):
        return reverse('contests:problem', args=[self.contest_id, self.number])


class ClarificationManager(models.Manager):
    def privileged(self, user):
        return self.get_queryset() if user.is_staff else self.filter(user=user)


class Clarification(models.Model):
    # TODO: Replace contest with problem_in_contest.
    contest    = models.ForeignKey(Contest, db_index=False)
    user       = models.ForeignKey(User, db_index=False)
    question   = models.TextField()
    answer     = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ClarificationManager()

    class Meta:
        db_table      = 'clarifications'
        get_latest_by = 'created_at'

    def has_answer(self):
        return bool(self.answer)

    has_answer.boolean = True

    def __str__(self):
        return self.question if len(self.question) <= 70 else self.question[:67] + '...'


class NotificationManager(models.Manager):
    def privileged(self, user):
        if user.is_staff:
            return self.get_queryset()
        return self.filter(visible=True, created_at__lte=timezone.now())


class Notification(models.Model):
    contest     = models.ForeignKey(Contest)
    description = models.TextField()
    visible     = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    objects = NotificationManager()

    class Meta:
        db_table      = 'notifications'
        get_latest_by = 'created_at'

    def __str__(self):
        return self.description if len(self.description) <= 70 else self.description[:67] + '...'


class Compiler(models.Model):
    name            = models.CharField(max_length=64)
    codename        = models.CharField(max_length=32)
    runner_codename = models.CharField(max_length=32)
    obsolete        = models.BooleanField(default=False)
    # TODO: Remove this field when old tester support is dropped.
    extension       = models.CharField(max_length=255)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    highlighter     = models.CharField(max_length=32)

    class Meta:
        db_table      = 'compilers'
        get_latest_by = 'created_at'

    def __str__(self):
        return self.name


class Attempt(models.Model):
    problem_in_contest = models.ForeignKey(ProblemInContest)
    user               = models.ForeignKey(User)
    source             = models.TextField()
    compiler           = models.ForeignKey(Compiler)
    time               = models.DateTimeField(auto_now_add=True)
    tester_name        = models.CharField(max_length=48, blank=True, default='')
    # TODO: SET NOT NULL.
    result             = models.CharField(max_length=36, blank=True, null=True, db_index=True)
    error_message      = models.TextField(blank=True, null=True) # NULL for optimization reason.
    # TODO: Make this field an integer (properly converting old attempts).
    used_time          = models.FloatField(blank=True, null=True)
    used_memory        = models.PositiveIntegerField(blank=True, null=True)
    checker_comment    = models.TextField(blank=True, default='')
    score              = models.FloatField(blank=True, null=True)
    # TODO: Remove this field.
    lock_version       = models.IntegerField(blank=True, null=True)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        db_table      = 'attempts'
        get_latest_by = 'time'

    @property
    def problem(self):
        return self.problem_in_contest.problem

    @property
    def contest(self):
        return self.problem_in_contest.contest

    @property
    def verdict(self):
        return self.result if self.score is None else '{0.score:.1f}%'.format(self)

    def __str__(self):
        return '[{0.id:05}/{0.problem.id:03}] {0.problem_in_contest} by {0.user}'.format(self)

    def get_absolute_url(self):
        return reverse('contests:attempt', args=[self.id])


class TestInfo(models.Model):
    attempt         = models.ForeignKey(Attempt)
    test_number     = models.PositiveIntegerField()
    result          = models.CharField(max_length=23, blank=True, default='')
    # TODO: Maybe make these fields non-nullable? TestInfos are immutable anyway.
    used_memory     = models.PositiveIntegerField(blank=True, null=True)
    used_time       = models.FloatField(blank=True, null=True)
    checker_comment = models.TextField(blank=True, default='')

    class Meta:
        db_table        = 'test_infos'
        # unique_together = ('attempt_id', 'test_number')

    def __str__(self):
        return '{0.attempt_id:05}:{0.test_number}'.format(self)
