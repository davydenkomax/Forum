from .models import Section

def get_sections(request):
    return {'get_sections': Section.objects.filter(active=True)}