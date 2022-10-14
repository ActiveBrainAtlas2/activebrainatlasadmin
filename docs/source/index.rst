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
   :titlesonly:
   :maxdepth: 2
   :caption: Brain
   
   Admin module <modules/brain/admin.rst>
   Brain forms <modules/brain/forms.rst> 
   Brain models (database columns) <modules/brain/models.rst> 
   REST API serializers <modules/brain/serializers.rst> 
   REST API endpoints <modules/brain/views.rst>

.. toctree::
   :maxdepth: 1
   :caption: Neuroglancer:
   :hidden:

   Neuroglancer admin module <modules/neuroglancer/admin.rst> 
   Module to admin annotations <modules/neuroglancer/annotation_manager.rst>
   Neuroglancer models (database columns) <modules/neuroglancer/models.rst> 
   REST API serializers <modules/neuroglancer/serializers.rst> 
   Neuroglancer tests <modules/neuroglancer/tests.rst>
   REST API endpoints <modules/neuroglancer/views.rst>
   Bulk annotation inserts <modules/neuroglancer/bulk_insert.rst>
   Align atlas tools <modules/neuroglancer/atlas.rst>

.. toctree::
   :maxdepth: 2
   :caption: Entity relationship diagram for the Active brain atlas database:
   
   Diagram showing database tables and columns <modules/erd.rst>
