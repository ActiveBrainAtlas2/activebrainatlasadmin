"""This module defines the forms necessary to perform the QC on the slides/scenes.
The user can rearrange, edit, and hide scenes with these forms.
"""
from django import forms
from django.db.models import Max
from django.forms import ModelChoiceField
from brain.models import Animal, Slide, SlideCziToTif


class AnimalForm(forms.Form):
    """Sets up fields for the select dropdown menu in forms.
    Animals are sorted by name.
    """
    prep_id = ModelChoiceField(label='Animal',
                               queryset=Animal.objects.all().order_by('prep_id'),
                               required=False,
                               widget=forms.Select(attrs={'onchange': 'id_list.submit();', 'class': 'form-control'}))

    class Meta:
        fields = ('prep_id',)

class AnimalChoiceField(forms.ModelChoiceField):
    """A simple class that returns the animal name.
    """
    def label_from_instance(self, obj):
        return obj.prep_id

def repeat_scene(FK_slide_id, inserts, scene_number):
    """ Helper method to duplicate a scene.

    :param FK_slide_id: An integer primary key of the slide.
    :param inserts: An integer defining how many scenes to insert.
    :param scene_number: An integer used to find the nearest neighbor
    """
    tifs = SlideCziToTif.objects.filter(slide__id=FK_slide_id).filter(active=True) \
        .filter(scene_number=scene_number)

    if not tifs:
        tifs = find_closest_neighbor(FK_slide_id, scene_number)

    for _ in range(inserts):
        create_scene(tifs, scene_number)


def remove_scene(FK_slide_id, deletes, scene_number):
    """ Helper method to remove a scene.

    :param FK_slide_id: An integer primary key of the slide.
    :param deletes: An integer defining how many scenes to delete.
    :param scene_number: An integer used to find the nearest neighbor
    """
    channels = SlideCziToTif.objects.filter(slide__id=FK_slide_id).filter(active=True).values('channel').distinct().count()
    for channeli in range(channels):
        tifs = SlideCziToTif.objects.filter(slide__id=FK_slide_id).filter(active=True) \
            .filter(scene_number=scene_number).filter(channel=channeli+1)[:deletes]
        for tif in tifs:
            tif.delete()


def create_scene(tifs, scene_number):
    """ Helper method to create a scene.

    :param tifs: A list of TIFFs.
    :param scene_number: An integer used to find the nearest neighbor
    """
    for tif in tifs:
        newtif = tif
        newtif.active = True
        newtif.pk = None
        newtif.scene_number = scene_number
        newtif.save()


def find_closest_neighbor(FK_slide_id, scene_number):
    """Helper method to get the nearest scene. Look first at the preceding tifs, 
        if nothing is there, go for the one just after.

    :param FK_slide_id:  primary key of the slide
    :param scene_number: scene number. 1 per set of 3 channels
    :return:  set of tifs
    """
    channels = SlideCziToTif.objects.filter(slide__id=FK_slide_id).filter(active=True).values('channel').distinct().count()
    below = SlideCziToTif.objects.filter(slide__id=FK_slide_id).filter(active=True) \
                .filter(scene_number__lt=scene_number).order_by('-scene_number')[:channels]
    if below.exists():
        tifs = below
    else:
        tifs = SlideCziToTif.objects.filter(slide__id=FK_slide_id).filter(active=True) \
                .filter(scene_number__gt=scene_number).order_by('scene_number')[:channels]

    return tifs


def set_scene_active_inactive(FK_slide_id, scene_number, active):
    """ Helper method to set a scene as active.

    :param FK_slide_id: An integer for the primary key of the slide.
    :param scene_number: An integer used to find the nearest neighbor.
    :param active: A boolean defining whether to set the scene active or inactive
    """
    tifs = SlideCziToTif.objects.filter(slide__id=FK_slide_id).filter(scene_number=scene_number).order_by('scene_number')
    for tif in tifs:
        tif.active = active
        tif.save()

def set_end(FK_slide_id, scene_number):
    """ Helper method to set a scene as the very last one in a brain.

    :param FK_slide_id: An integer for the primary key of the slide.
    :param scene_number: An integer used to find the nearest neighbor.
    """
    tifs = SlideCziToTif.objects.filter(slide__id=FK_slide_id).filter(scene_number__gte=scene_number)
    for tif in tifs:
        tif.active = False
        tif.save()


def scene_reorder(FK_slide_id):
    """ Helper method to reorder a set of scenes.

    :param FK_slide_id: An integer for the primary key of the slide.
    """
    scenes_tifs = SlideCziToTif.objects.filter(slide__id=FK_slide_id).filter(active=True).order_by('scene_number')
    channels = SlideCziToTif.objects.filter(slide__id=FK_slide_id).filter(active=True).values('channel').distinct().count()
    len_tifs = len(scenes_tifs) + 1
    flattened = [item for sublist in [[i] * channels for i in range(1, len_tifs)] for item in sublist]

    for new_scene, tif in zip(flattened, scenes_tifs):  # iterate over the scenes
        tif.scene_number = new_scene
        tif.save()

def save_slide_model(self, request, obj, form, change):
    """This method overrides the slide save method.

    :param request: The HTTP request.
    :param obj: The slide object.
    :param form: The form object.
    :param change: unused variable, shows if the form has changed.
    """
    scene_numbers = [1, 2, 3, 4, 5, 6]
    qc_1 = form.cleaned_data.get('scene_qc_1')
    qc_2 = form.cleaned_data.get('scene_qc_2')
    qc_3 = form.cleaned_data.get('scene_qc_3')
    qc_4 = form.cleaned_data.get('scene_qc_4')
    qc_5 = form.cleaned_data.get('scene_qc_5')
    qc_6 = form.cleaned_data.get('scene_qc_6')


    # do the QC fields
    OUTOFFOCUS = 1
    BADTISSUE = 2
    END = 3
    OK = 0
    qc_values = [qc_1, qc_2, qc_3, qc_4, qc_5, qc_6]
    current_qcs = Slide.objects.values_list('scene_qc_1', 'scene_qc_2', 'scene_qc_3',
                                            'scene_qc_4', 'scene_qc_5',
                                            'scene_qc_6').get(pk=obj.id)
    # this top loop needs to be run before the 2nd loop to make sure the required
    # tifs get set to inactive before finding a nearest neighbour
    for qc_value, current_qc, scene_number in zip(qc_values, current_qcs, scene_numbers):
        if qc_value in [OUTOFFOCUS, BADTISSUE] and qc_value != current_qc:
            set_scene_active_inactive(obj.id, scene_number, False)
    # tifs get set to active to back out a mistake
    for qc_value, current_qc, scene_number in zip(qc_values, current_qcs, scene_numbers):
        if qc_value == OK and qc_value != current_qc:
            set_scene_active_inactive(obj.id, scene_number, True)

    for qc_value, current_qc, scene_number in zip(qc_values, current_qcs, scene_numbers):
        if qc_value == END and qc_value != current_qc:
            set_end(obj.id, scene_number)

    form_names = ['insert_before_one', 'insert_between_one_two', 'insert_between_two_three',
                  'insert_between_three_four', 'insert_between_four_five', 'insert_between_five_six']
    insert_values = [form.cleaned_data.get(name) for name in form_names]

    # moves = sum([value for value in insert_values if value is not None])
    # scene_count = obj.scenes
    # scenes = range(1, scene_count + 1)
    ## do the inserts
    current_values = Slide.objects.values_list('insert_before_one', 'insert_between_one_two',
                                               'insert_between_two_three',
                                               'insert_between_three_four', 'insert_between_four_five',
                                               'insert_between_five_six').get(pk=obj.id)

    for new, current, scene_number in zip(insert_values, current_values, scene_numbers):
        if new is not None and new > current:
            difference = new - current
            repeat_scene(obj.id, difference, scene_number)
        if new is not None and new < current:
            difference = current - new
            remove_scene(obj.id, difference, scene_number)

    scene_reorder(obj.id)


    obj.scenes = SlideCziToTif.objects.filter(slide__id=obj.id).filter(channel=1).filter(active=True).count()

class TifInlineFormset(forms.models.BaseInlineFormSet):
    """This class defines the form for the subsets of scenes for a slide.
    This is where the work is done for rearranging and editing the scenes.
    """

    def save_existing(self, form, instance, commit=True):
        """This is called when updating an instance.

        :param form: Form object.
        :param instance: slide CZI TIFF object.
        :param commit: A boolean stating if the object should be committed.
        """
        obj = super(TifInlineFormset, self).save_existing(form, instance, commit=False)
        ch23s = SlideCziToTif.objects.filter(slide__id=obj.FK_slide_id).filter(scene_number=obj.scene_number).filter(scene_index=obj.scene_index)
        for ch23 in ch23s:
            ch23.active = False
            ch23.save()
        scene_reorder(obj.FK_slide_id)
        if commit:
            obj.save()
        return obj

