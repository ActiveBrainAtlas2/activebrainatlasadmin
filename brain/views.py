from django.shortcuts import render
from brain.models import Animal, Section
from brain.forms import AnimalForm

# from url initial page
def image_list(request):
    prep_id = request.GET.get('prep_id')
    form = AnimalForm()  # A form bound to the GET data
    animals = Animal.objects.filter(prep_id=prep_id).order_by('prep_id')
    sections = None
    title = 'Select an animal from the dropdown menu.'
    if prep_id:
        title = 'Thumbnail images for: {}'.format(prep_id)
        sections = Section.objects.filter(prep_id=prep_id).order_by('file_name')



    return render(request, 'list.html',{'animals': animals,
                                        'sections': sections,
                                        'form': form,
                                        'prep_id': prep_id,
                                        'title': title})

