from django import forms

from .models import Wikipage
from .models import Expert
from .models import Publication
from .models import Expertwikipub
from .models import Expertwikipubreferee
from .models import Expertkeywords
from .models import SimilarExpert
from .models import StudyStatistic
from .models import Publicationkeyword
from .models import Locationtimezone

# class UploadFileForm(forms.Form):
#     title = forms.CharField(max_length=50)
#     file = forms.FileField()

class ExpertForm(forms.ModelForm):
    class Meta:
        model = Expert
        fields = ['name', 'email']