# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django_mysql.models import EnumField

class AtlasModel(models.Model):
    active = models.IntegerField(default = 1, editable = False)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True

class Animal(AtlasModel):
    prep_id = models.CharField(primary_key=True, max_length=20)
    performance_center = EnumField(choices=['CSHL','Salk','UCSD','HHMI','Duke'], blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    species = models.CharField(max_length=5, blank=True, null=True)
    strain = EnumField(choices=['mouse','rat'], blank=True, null=True)
    sex = EnumField(choices=['M','F'], blank=True, null=True)
    genotype = models.CharField(max_length=100, blank=True, null=True)
    breeder_line = models.CharField(max_length=100, blank=True, null=True)
    vender = EnumField(choices=['Jackson','Charles River','Harlan','NIH','Taconic'], blank=True, null=True)
    stock_number = models.CharField(max_length=100, blank=True, null=True)
    tissue_source = EnumField(choices=['animal','brain','slides'], blank=True, null=True)
    ship_date = models.DateField(blank=True, null=True)
    shipper = EnumField(choices=['FedEx','UPS'], blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    aliases_1 = models.CharField(max_length=100, blank=True, null=True)
    aliases_2 = models.CharField(max_length=100, blank=True, null=True)
    aliases_3 = models.CharField(max_length=100, blank=True, null=True)
    aliases_4 = models.CharField(max_length=100, blank=True, null=True)
    aliases_5 = models.CharField(max_length=100, blank=True, null=True)
    comments = models.CharField(max_length=2001, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'animal'
        verbose_name = 'Animal'
        verbose_name_plural = 'Animals'
 

class FileOperation(AtlasModel):
    tif = models.ForeignKey('SlideCziToTif', models.DO_NOTHING)
    operation = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    file_size = models.FloatField()
    active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'file_operation'
        verbose_name = 'File Operation'
        verbose_name_plural = 'File Operations'


class Histology(AtlasModel):
    prep = models.ForeignKey(Animal, models.DO_NOTHING)
    virus = models.ForeignKey('Virus', models.DO_NOTHING, blank=True, null=True)
    label = models.ForeignKey('OrganicLabel', models.DO_NOTHING, blank=True, null=True)
    performance_center = EnumField(choices=['FedEx','UPS'], blank=True, null=True)
    anesthesia = EnumField(choices=['ketamine','isoflurane','pentobarbital','fatal plus'], blank=True, null=True)
    perfusion_age_in_days = models.PositiveIntegerField()
    perfusion_date = models.DateField(blank=True, null=True)
    exsangination_method = EnumField(choices=['PBS','aCSF','Ringers'], blank=True, null=True)
    fixative_method = EnumField(choices=['Para','Glut','Post fix'], blank=True, null=True)
    special_perfusion_notes = models.CharField(max_length=200, blank=True, null=True)
    post_fixation_period = models.PositiveIntegerField()
    whole_brain = models.CharField(max_length=1, blank=True, null=True)
    block = models.CharField(max_length=200, blank=True, null=True)
    date_sectioned = models.DateField(blank=True, null=True)
    sectioning_method = EnumField(choices=['cryoJane','cryostat','vibratome','optical','sliding microtiome'], blank=True, null=True)
    section_thickness = models.PositiveIntegerField()
    orientation = EnumField(choices=['coronal','horizontal','sagittal','oblique'], blank=True, null=True)
    oblique_notes = models.CharField(max_length=200, blank=True, null=True)
    mounting = EnumField(choices=['every section','2nd','3rd','4th','5ft','6th'], blank=True, null=True)
    counterstain = EnumField(choices=['thionon','NtB','NtFR','DAPI','Giemsa','Syto41'], blank=True, null=True)
    comments = models.CharField(max_length=2001, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'histology'
        verbose_name = 'Histology'
        verbose_name_plural = 'Histologies'


class Injection(AtlasModel):
    prep = models.ForeignKey(Animal, models.DO_NOTHING)
    label = models.ForeignKey('OrganicLabel', models.DO_NOTHING, blank=True, null=True)
    performance_center = EnumField(choices=['CSHL','Salk','UCSD','HHMI','Duke'], blank=True, null=True)
    anesthesia = EnumField(choices=['ketamine','isoflurane'], blank=True, null=True)
    method = EnumField(choices=['iontophoresis','pressure','volume'], blank=True, null=True)
    injection_volume = models.FloatField()
    pipet = EnumField(choices=['glass','quartz','Hamilton','syringe needle'], blank=True, null=True)
    location = models.CharField(max_length=20, blank=True, null=True)
    angle = models.CharField(max_length=20, blank=True, null=True)
    brain_location_dv = models.FloatField()
    brain_location_ml = models.FloatField()
    brain_location_ap = models.FloatField()
    injection_date = models.DateField(blank=True, null=True)
    transport_days = models.IntegerField()
    virus_count = models.IntegerField()
    comments = models.CharField(max_length=2001, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'injection'
        verbose_name = 'Injection'
        verbose_name_plural = 'Injections'
        
    def __str__(self):
        return "{} {}".format(self.prep.prep_id, self.comments)
        


class InjectionVirus(AtlasModel):
    injection = models.ForeignKey(Injection, models.DO_NOTHING)
    virus = models.ForeignKey('Virus', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'injection_virus'
        verbose_name = 'Injection Virus'
        verbose_name_plural = 'Injection Viruses'


class OrganicLabel(AtlasModel):
    label_id = models.CharField(max_length=20)
    label_type = EnumField(choices=['Cascade Blue','Chicago Blue','Alexa405','Alexa488','Alexa647','Cy2','Cy3','Cy5','Cy5.5','Cy7','Fluorescein','Rhodamine B','Rhodamine 6G','Texas Red','TMR'], blank=True, null=True)
    type_lot_number = models.CharField(max_length=20, blank=True, null=True)
    type_tracer = EnumField(choices=['BDA','Dextran','FluoroGold','DiI','DiO'], blank=True, null=True)
    type_details = models.CharField(max_length=500, blank=True, null=True)
    concentration = models.FloatField()
    excitation_1p_wavelength = models.IntegerField()
    excitation_1p_range = models.IntegerField()
    excitation_2p_wavelength = models.IntegerField()
    excitation_2p_range = models.IntegerField()
    lp_dichroic_cut = models.IntegerField()
    emission_wavelength = models.IntegerField()
    emission_range = models.IntegerField()
    label_source = EnumField(choices=['Invitrogen','Sigma','Thermo-Fisher'], blank=True, null=True)
    source_details = models.CharField(max_length=100, blank=True, null=True)
    comments = models.CharField(max_length=2000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'organic_label'


class RowSequence(models.Model):
    counter = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'row_sequence'


class ScanRun(AtlasModel):
    prep = models.ForeignKey(Animal, models.DO_NOTHING)
    performance_center = EnumField(choices=['CSHL','Salk','UCSD','HHMI'], blank=True, null=True)
    machine = EnumField(choices=['Invitrogen','Sigma','Thermo-Fisher'], blank=True, null=True)
    objective = EnumField(choices=['60X','40X','20X','10X'], blank=True, null=True)
    resolution = models.FloatField()
    number_of_slides = models.IntegerField()
    scan_date = models.DateField(blank=True, null=True)
    file_type = EnumField(choices=['CZI','JPEG2000','NDPI','NGR'], blank=True, null=True)
    scenes_per_slide = EnumField(choices=['1','2','3','4','5','6'], blank=True, null=True)
    section_schema = EnumField(choices=['L to R','R to L'], blank=True, null=True)
    channels_per_scene = EnumField(choices=['1','2','3','4'], blank=True, null=True)
    slide_folder_path = models.CharField(max_length=200, blank=True, null=True)
    converted_folder_path = models.CharField(max_length=200, blank=True, null=True)
    converted_status = EnumField(choices=['not started','converted','converting','error'], blank=True, null=True)
    ch_1_filter_set = EnumField(choices=['68','47','38','46','63','64','50'], blank=True, null=True)
    ch_2_filter_set = EnumField(choices=['68','47','38','46','63','64','50'], blank=True, null=True)
    ch_3_filter_set = EnumField(choices=['68','47','38','46','63','64','50'], blank=True, null=True)
    ch_4_filter_set = EnumField(choices=['68','47','38','46','63','64','50'], blank=True, null=True)
    comments = models.CharField(max_length=2001, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'scan_run'


class Slide(AtlasModel):
    scan_run = models.ForeignKey(ScanRun, models.DO_NOTHING)
    slide_physical_id = models.IntegerField()
    rescan_number = models.CharField(max_length=1)
    slide_status = EnumField(choices=['Bad','Good'], blank=False, null=False)
    scene_qc_1 = EnumField(choices=['','Missing one section','two','three','four','five','six','O-o-F','Bad tissue'])
    scene_qc_2 = EnumField(choices=['','Missing one section','two','three','four','five','six','O-o-F','Bad tissue'])
    scene_qc_3 = EnumField(choices=['','Missing one section','two','three','four','five','six','O-o-F','Bad tissue'])
    scene_qc_4 = EnumField(choices=['','Missing one section','two','three','four','five','six','O-o-F','Bad tissue'])
    scene_qc_5 = EnumField(choices=['','Missing one section','two','three','four','five','six','O-o-F','Bad tissue'])
    scene_qc_6 = EnumField(choices=['','Missing one section','two','three','four','five','six','O-o-F','Bad tissue'])
    file_name = models.CharField(max_length=200)
    comments = models.CharField(max_length=2001, blank=True, null=True)
    file_size = models.FloatField()
    processing_duration = models.FloatField()
    processed = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'slide'


class SlideCziToTif(AtlasModel):
    slide = models.ForeignKey(Slide, models.DO_NOTHING)
    file_name = models.CharField(max_length=200)
    scene_number = models.IntegerField()
    channel = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    comments = models.CharField(max_length=2000, blank=True, null=True)
    file_size = models.FloatField()

    class Meta:
        managed = False
        db_table = 'slide_czi_to_tif'
        verbose_name = 'Slide CZI to TIF'
        verbose_name_plural = 'Slides CZI to TIF'


class Virus(AtlasModel):
    virus_name = models.CharField(max_length=50)
    virus_type = EnumField(choices=['Adenovirus','AAV','CAV','DG rabies','G-pseudo-Lenti','Herpes','Lenti','N2C rabies','Sinbis'], blank=True, null=True)
    virus_active = EnumField(choices=['yes','no'], blank=True, null=True)
    type_details = models.CharField(max_length=500, blank=True, null=True)
    titer = models.FloatField()
    lot_number = models.CharField(max_length=20, blank=True, null=True)
    label = EnumField(choices=['YFP','GFP','RFP','histo-tag'], blank=True, null=True)
    label2 = models.CharField(max_length=200, blank=True, null=True)
    excitation_1p_wavelength = models.IntegerField()
    excitation_1p_range = models.IntegerField()
    excitation_2p_wavelength = models.IntegerField()
    excitation_2p_range = models.IntegerField()
    lp_dichroic_cut = models.IntegerField()
    emission_wavelength = models.IntegerField()
    emission_range = models.IntegerField()
    virus_source = EnumField(choices=['Adgene','Salk','Penn','UNC'], blank=True, null=True)
    source_details = models.CharField(max_length=100, blank=True, null=True)
    comments = models.CharField(max_length=2000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'virus'
        verbose_name = 'Virus'
        verbose_name_plural = 'Viruses'
        
    def __str__(self):
        return self.virus_name
