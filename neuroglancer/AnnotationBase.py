from django.contrib.auth.models import User
from brain.models import Animal
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
class AnnotationBase:
    def set_annotator_from_id(self,user_id):
        try:
            self.annotator = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            logger.error("User does not exist")
            return
    def set_animal_from_id(self,animal_id):
        try:
            self.animal = Animal.objects.get(pk=animal_id)
        except Animal.DoesNotExist:
            logger.error("Animal does not exist")
            return
    
    def set_animal_from_animal_name(self,animal_name):
        try:
            self.animal = Animal.objects.filter(prep_id=animal_name).first()
        except Animal.DoesNotExist:
            logger.error("Animal does not exist")
            return