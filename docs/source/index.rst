.. ActiveBrainAtlas documentation master file, created by
   sphinx-quickstart on Wed Jun  1 15:07:58 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

The ActiveBrainAtlas's documentation
============================================
These pages contain documentation regarding the MVC (model, view, and controller) programming
classes for the Django database interface. Django breaks up this interface into 'apps'.

These apps contain classes for each of the MVC components. The models.py file contains classes
that describe a database schema table.


****

.. toctree::
   :maxdepth: 2
   :caption: ERD:
   
   modules/erd.rst

.. toctree::
   :maxdepth: 2
   :caption: Brain:

   modules/brain/admin.rst
   modules/brain/models.rst
   modules/brain/serializers.rst
   modules/brain/views.rst

.. toctree::
   :maxdepth: 2
   :caption: Neuroglancer:

   modules/neuroglancer/admin.rst
   modules/neuroglancer/annotation_manager.rst
   modules/neuroglancer/models.rst
   modules/neuroglancer/serializers.rst
   modules/neuroglancer/tests.rst
   modules/neuroglancer/views.rst
