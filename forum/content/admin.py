from django.contrib import admin
from .models import Section, Subject, Message, Text, Content, Image

# Register your models here.
@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    list_filter = ['active']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['author', 'section', 'name', 'created']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['created']
    search_fields = ['name']

@admin.register(Message)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['subject', 'author', 'parent_message']
    list_filter = ['created']

@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ['text']

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['file']


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['message']