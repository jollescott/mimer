from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models

class QuizUserAdmin(UserAdmin):
    model = models.QuizUser

    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('overall_score', 'sana'),}),
    )

# Register your models here.
admin.site.register(models.QuizUser, QuizUserAdmin)
admin.site.register(models.Test)
admin.site.register(models.Alternative)
admin.site.register(models.Answer)
admin.site.register(models.Asset)
