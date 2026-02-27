from django.contrib import admin
from django.utils.safestring import mark_safe
import nested_admin
from .models import Presentation, Guide, Video, Topic, Practical, Test, Question, Choice, TestAttempt, Answer
from .forms import TestForm


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'order', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'description')
    ordering = ('order',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Practical)
class PracticalAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published')
    prepopulated_fields = {'slug': ('title',)}



class ChoiceInline(nested_admin.NestedTabularInline):
    model = Choice
    extra = 1


class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    extra = 1
    inlines = [ChoiceInline]
    fields = ('text', 'order', 'points', 'allow_multiple')


@admin.register(Test)
class TestAdmin(nested_admin.NestedModelAdmin):
    list_display = ('title', 'file', 'is_published', 'created_at')
    search_fields = ('title',)
    # include question inline so questions and their choices can be edited when editing a Test
    inlines = [QuestionInline]
    form = TestForm
    # keep Test visible as the single test entry in admin


# We no longer register Question and Choice as top-level admin models; they are managed
# via nested inlines inside TestAdmin. If they were previously registered, unregister them.
try:
    admin.site.unregister(Question)
except Exception:
    pass

try:
    admin.site.unregister(Choice)
except Exception:
    pass


try:
    admin.site.unregister(TestAttempt)
except Exception:
    pass

try:
    admin.site.unregister(Answer)
except Exception:
    pass

# Remove top-level Question and Choice entries so admin shows Test as the primary place
# to add tests and questions (choices are edited via the Question change page).
try:
    admin.site.unregister(Question)
except Exception:
    pass

try:
    admin.site.unregister(Choice)
except Exception:
    pass



# Uzbek admin branding
admin.site.site_header = "ANIQ QISHLOQ XO'JALIGI — Admin"
admin.site.site_title = "AQX Admin"
admin.site.index_title = "Sayt bo'limlari"

