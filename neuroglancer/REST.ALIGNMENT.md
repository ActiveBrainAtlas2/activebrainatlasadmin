# How Neuroglancer Aligns a Brain to the Atlas
1. User selects a brain from a dropdown menu which has 3 variables to send to the REST API.
    1. Brain ID
    1. Input type (currently we are only using the 'corrected' COMs)
    1. User ID (currently this defaults to Beth as she did all the manual entry of the COMs)
1. Neuroglancer makes a REST call via this url:  https://activebrainatlas.ucsd.edu/activebrainatlas/rotation/DK39/corrected/2
1. In the url above, DK39 is the Brain ID, 'corrected' is the input type and 2 is Beth's ID.
1. That url then calls the rotation method in this file: [views.py](views.py)