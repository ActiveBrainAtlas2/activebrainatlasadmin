# Testing
This page contains inforamtion about the main repositories in the Active Brain Atlas repository and the tests related to modules in each repository.
## Active Brain Atlas (Django)
Active brain atlas is the django repository that provides the API end points and admin website access to the database.  

To run the test in this repository, set the test database to auto_tests in the setting.py file by adding `'TEST': {'NAME': 'auto_tests'},` to database settings and run `python manage.py --keepdb test neuroglancer`

The Django repository consists of individual apps. The functions of each and the related tests are outlined below:

### Neuroglancer App
   Handles the storage of neuroglancer session states, parses and stores the user annotations created in these sessions.  

{[test.py](https://github.com/ActiveBrainAtlas2/activebrainatlasadmin/blob/master/neuroglancer/tests.py)}  Tests various API end points related to querying the list of available neuroglancer states, annotations, transformations and add user annotations.  See details in documentations

## Pre-processing Pipeline
The preprocesing pipeline turns Zeiss microscope images in CZI format to the Seung lab precomputed neuroglancer formats 

--No Tests so far

## Abakit
Abakit contains a set of commonly used tool in both Django and Pre-processing repository.  The modules include main classes in Atlas creation, contouring, brain registration and transforamation.

{[test_ng_segment_maker.py](https://github.com/ActiveBrainAtlas2/abakit/blob/master/src/abakit/atlas/tests/test_ng_segment_maker.py)}  Tests the ability Ng segment maker class that turns a 3D mask array into the Seung lab precomputed segmentation layer format.  A segmentation layer is a neuroglancer layer that displays 3D volumes.  The test create a mockup 3D volume, turns it into the precomputed format, and check that the correct set of folders are created.

{[test_volume_maker.py](https://github.com/ActiveBrainAtlas2/abakit/blob/master/src/abakit/atlas/tests/test_volume_maker.py)}  Tests the VolumeMaker class which turns a set of contours to a 3D mask.  The class finds the smallest bounding box for the shape and returns a origin in the same coordinate of the contours that signals where the 3D mask should be placed.  The test create a set of mockup contours and checks if the correct 3d mask is created.

{[test_volume_to_contour.py](https://github.com/ActiveBrainAtlas2/abakit/blob/master/src/abakit/atlas/tests/test_volume_to_contour.py)}  Tests the VolumeToContour class which turns a 3D mask to a set of contours.  The test create a mockup volume and checks if the correct contours are generated.

{[test_transformation.py](https://github.com/ActiveBrainAtlas2/abakit/blob/master/src/abakit/atlas/tests/test_volume_to_contour.py)} Tests the transformation class used to store the Stack to Atlas or Atlas to Stack transforms.  The test retrives one of the transformation from the database, applies the forward and reverse transform to a group of random points, and check if the same points are recovered.
