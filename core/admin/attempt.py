from ajax_select              import make_ajax_form
from django                   import forms
from django.contrib           import admin
from django.utils.translation import ugettext as _

from jquery_model_admin import JQueryModelAdmin

from .. import models


@admin.register(models.Attempt)
class AttemptAdmin(admin.ModelAdmin, JQueryModelAdmin):
    form = make_ajax_form(
        models.Attempt, {
            "user": "users",
            "problem_in_contest": "problems_in_contests",
        }
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            (
                None, {
                    "fields": ("user", "problem_in_contest", "compiler", "source"),
                }
            ), (
                _("Results"), {
                    "fields": (("result", "score"), ("used_time", "used_memory"), "error_message"),
                }
            ), (
                _("Rails trash"), {
                    "fields": ["lock_version"],
                    "classes": ["collapse"],
                }
            ),
        )
        if obj is not None:
            fieldsets += (
                (
                    _("Statistics"), {
                        "fields": self.readonly_fields,
                    }
                ),
            )
        return fieldsets

    readonly_fields = ("time", "updated_at")
    list_display = (
        "id", "user", "problem", "compiler", "contest", "verdict", "time",
        "used_time", "used_memory",
    )
    # list_filter = [("user", admin.RelatedOnlyFieldListFilter)]
    list_display_links = ("id", "user", "problem")
    date_hierarchy = "time"

    # actions = ()

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            "user", "problem_in_contest__problem", "problem_in_contest__contest",
        )