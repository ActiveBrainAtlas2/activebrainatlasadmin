from neuroglancer.models import LayerData
from ajax_datatable.views import AjaxDatatableView
from django.db.models import Sum, Count, Max, Q



class LayerDataView(AjaxDatatableView):

    model = LayerData
    title = 'Ajax Annotations'
    initial_order = [["animal", "asc"], ]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'

    column_defs = [
        AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'visible': False, },
        {'name': 'animal', 'foreign_field': 'prep__prep_id', 'visible': True, 'title':'junk'},
        {'name': 'layer', 'visible': True, },
        {'name': 'user', 'foreign_field': 'person__username','visible': True, },
        {'name': 'updated',  'visible': True, 'searchable': False},
        {'name': 'input_type', 'foreign_field': 'input_type__input_type', 'visible': True, },
    ]

    metrics = {
        'total': Count('id'),
        'updated': Max('updated')
    }


    def get_initial_queryset(self, request=None):
        # Optimization: Reduce the number of queries due to ManyToMany "tags" relation
        return LayerData.objects.filter(active=True)
        


    """
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


    def customize_row(self, row, obj):
        # 'row' is a dictionary representing the current row, and 'obj' is the current object.
        # Display tags as a list of strings
        row['tags'] = ','.join( [t.name for t in obj.tags.all()])
        return
    """