from django.http import JsonResponse
from .models import Tag
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def tag_autocomplete(request):
    '''Simple autocomplete wrapper for jQuery GUI Tags'''
    tags = Tag.objects.filter(name__icontains=request.GET.get('term'))
    name_list = []
    for tag in tags:
        name_list.append(tag.name)
    return JsonResponse(name_list, safe=False)
