from django.contrib import admin

# Register your models here.
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


class WikipageAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'edit_protection_level', 'views_last_90_days', 'timestamp', 'updated']

    search_fields = ['title']

    class Meta:
        model = Wikipage

admin.site.register(Wikipage, WikipageAdmin)


class ExpertAdmin(admin.ModelAdmin):
    list_display = ['id', 'firstname', 'name', 'email', 'domain', 'specialization', 'school', 'location',
        'indiscipline', 'inspecialtyarea', 'study_version', 'private_first', 'citedpublication', 'relevance_factor',
        'likely_to_cite', 'may_include_reference', 'might_refer_to', 'relevant_to_research', 'within_area',
        'on_expertise_topic', 'highviewspast90days', 'especially_popular', 'highly_visible', 
        'highly_popular', 'econ_wikiproject_clicked', 'withdrawal', 'returned', 'emailCount', 'phase1',
        'phase2', 'phase3', 'email1Count', 'email2Count', 'email3Count', 'emailSent', 'email1Sent',
        'email2Sent', 'email3Sent', 'email1_opened', 'email1OpenedTime', 'email2_opened',
        'email2OpenedTime', 'email3_opened', 'email3OpenedTime', 'emailCommunication', 'article_clicked',
        'talkpage_clicked', 'post_clicked', 'tutorial_clicked', 'timestamp', 'updated']

    search_fields = ['id', 'firstname', 'name', 'email']

    readonly_fields = ('id', 'email1Sent', 'email2Sent', 'email3Sent', 'email1OpenedTime', 'email2OpenedTime',
        'email3OpenedTime', )

    class Meta:
        model = Expert

admin.site.register(Expert, ExpertAdmin)


class PublicationAdmin(admin.ModelAdmin):
    list_display = ['title', 'citations', 'publication_year', 'url', 'fullcitation', 'timestamp', 'updated']

    search_fields = ['title', 'fullcitation']

    class Meta:
        model = Publication

admin.site.register(Publication, PublicationAdmin)


class ExpertwikipubAdmin(admin.ModelAdmin):
    list_display = ['id', 'expert', 'wikipage', 'publication', 'link_clicked', 'last_name_ocurances',
        'related_publications_number', 'rating', 'comment', 'submittedtotalkpage', 'approvedbywikipedians',
        'rejectedbywikipedians', 'timestamp', 'updated']

    search_fields = ['id', 'expert__firstname', 'expert__name', 'expert__email',
        'wikipage__title', 'publication__title', 'publication__citations']

    class Meta:
        model = Expertwikipub

admin.site.register(Expertwikipub, ExpertwikipubAdmin)


class ExpertwikipubrefereeAdmin(admin.ModelAdmin):
    list_display = ['expertwikipub', 'name', 'email', 'timestamp', 'updated']

    search_fields = ['title']

    class Meta:
        model = Expertwikipubreferee

admin.site.register(Expertwikipubreferee, ExpertwikipubrefereeAdmin)


class LocationtimezoneAdmin(admin.ModelAdmin):
    list_display = ['location', 'timezone', 'latitude', 'longitude']

    search_fields = ['location']

    class Meta:
        model = Locationtimezone

admin.site.register(Locationtimezone, LocationtimezoneAdmin)


class ExpertkeywordsAdmin(admin.ModelAdmin):
    list_display = ['expert', 'keyword', 'used', 'timestamp', 'updated']
    class Meta:
        model = Expertkeywords

admin.site.register(Expertkeywords, ExpertkeywordsAdmin)


class SimilarExpertAdmin(admin.ModelAdmin):
    list_display = ['expert', 'relatedexpert', 'timestamp', 'updated']
    class Meta:
        model = SimilarExpert

admin.site.register(SimilarExpert, SimilarExpertAdmin)


class StudyStatisticAdmin(admin.ModelAdmin):
    list_display = ['domain',
        'disciplinetotalnumphase1', 'disciplinelinkclickednumphase1', 'disciplineresponsenumphase1',
        'specialtytotalnumphase1', 'specialtylinkclickednumphase1', 'specialtyresponsenumphase1',
        'viewstotalnumphase1', 'viewslinkclickednumphase1', 'viewsresponsenumphase1',
        'citedpublicationtotalnumphase1', 'citedpublicationlinkclickednumphase1', 'citedpublicationresponsenumphase1',
        'grouptotalnumphase1', 'grouplinkclickednumphase1', 'groupresponsenumphase1',
        'disciplinetotalnumphase2', 'disciplinelinkclickednumphase2', 'disciplineresponsenumphase2',
        'specialtytotalnumphase2', 'specialtylinkclickednumphase2', 'specialtyresponsenumphase2',
        'viewstotalnumphase2', 'viewslinkclickednumphase2', 'viewsresponsenumphase2',
        'grouptotalnumphase2', 'grouplinkclickednumphase2', 'groupresponsenumphase2',
        'citedpublicationtotalnumphase2', 'citedpublicationlinkclickednumphase2', 'citedpublicationresponsenumphase2',
        'timestamp', 'updated']
    class Meta:
        model = StudyStatistic

admin.site.register(StudyStatistic, StudyStatisticAdmin)
