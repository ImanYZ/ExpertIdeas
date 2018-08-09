from django.db import models
from django.utils.encoding import smart_unicode

class Wikipage(models.Model):
    # article_id is a required value in the database (null) and in the form (blank). We can get rid of both parameters as they are False.
    article_id = models.BigIntegerField(null=False, blank=False)
    title = models.CharField(max_length=256, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    edit_protection_level = models.CharField(max_length=25, null=True, blank=True)
    quality_class = models.CharField(max_length=25, null=True, blank=True)
    importance_class = models.CharField(max_length=25, null=True, blank=True)
    page_length = models.PositiveIntegerField(null=True, blank=True)
    watchers = models.PositiveIntegerField(null=True, blank=True)
    last_edit_time = models.DateTimeField(null=True, blank=True)
    creation_time = models.DateTimeField(null=True, blank=True)
    redirects = models.PositiveIntegerField(null=True, blank=True)
    total_edits = models.PositiveIntegerField(null=True, blank=True)
    distinct_authors = models.PositiveIntegerField(null=True, blank=True)
    last_month_total_edits = models.PositiveIntegerField(null=True, blank=True)
    last_month_distinct_authors = models.PositiveIntegerField(null=True, blank=True)
    minor_edits = models.PositiveIntegerField(null=True, blank=True)
    average_time_between_edits = models.PositiveIntegerField(null=True, blank=True)
    average_edits_number_per_month = models.PositiveIntegerField(null=True, blank=True)
    average_edits_number_per_year = models.PositiveIntegerField(null=True, blank=True)
    last_day_edits = models.PositiveIntegerField(null=True, blank=True)
    last_week_edits = models.PositiveIntegerField(null=True, blank=True)
    last_month_edits = models.PositiveIntegerField(null=True, blank=True)
    last_year_edits = models.PositiveIntegerField(null=True, blank=True)
    links_to_this_page = models.PositiveIntegerField(null=True, blank=True)
    views_last_90_days = models.PositiveIntegerField(null=True, blank=True)
    total_references = models.PositiveIntegerField(null=True, blank=True)
    external_hyperlinks = models.PositiveIntegerField(null=True, blank=True)

    # auto_now_add=True means it will return the date and time when the user signedup, and auto_now means it will return the date and time when it's updated.
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    # Solves thge problem with latin and other characters.
    def __unicode__(self):
        return smart_unicode(self.title)

    class Meta:
        ordering = ('title',)

class Expert(models.Model):
    name = models.CharField(max_length=256, null=True, blank=True)
    school = models.CharField(max_length=256, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    domain = models.CharField(max_length=128, null=True, blank=True)
    title = models.CharField(max_length=256, null=True, blank=True)
    specialization = models.CharField(max_length=256, null=True, blank=True)
    citations = models.PositiveIntegerField(null=True, blank=True)
    HIndex = models.PositiveIntegerField(null=True, blank=True)
    I10Index = models.PositiveIntegerField(null=True, blank=True)
    ip_address = models.CharField(max_length=120, null=True, blank=True)
    emailSent = models.DateTimeField(auto_now_add=True, auto_now=False)
    emailCount = models.PositiveIntegerField(default=0)
    withdrawal = models.BooleanField(default=False)
    returned = models.BooleanField(default=False)
    indiscipline = models.BooleanField(default=False)
    inspecialtyarea = models.BooleanField(default=False)
    citedpublication = models.BooleanField(default=False)
    highviewspast90days = models.BooleanField(default=False)
    phase1 = models.BooleanField(default=False)
    phase2 = models.BooleanField(default=False)
    firstname = models.CharField(max_length=256, null=True, blank=True)
    email1_opened = models.BooleanField(default=False)
    email2_opened = models.BooleanField(default=False)
    user_agent = models.CharField(max_length=512, null=True, blank=True)
    location = models.CharField(max_length=256, null=True, blank=True)
    email1Sent = models.DateTimeField(auto_now_add=True, auto_now=False)
    email1OpenedTime = models.DateTimeField(auto_now_add=True, auto_now=False)
    email2OpenedTime = models.DateTimeField(auto_now_add=True, auto_now=False)
    commentTime = models.DateTimeField(auto_now_add=True, auto_now=False)
    emailCommunication = models.BooleanField(default=False)
    email2Sent = models.DateTimeField(auto_now_add=True, auto_now=False)
    email3Sent = models.DateTimeField(auto_now_add=True, auto_now=False)
    phase3 = models.BooleanField(default=False)
    email3_opened = models.BooleanField(default=False)
    email3OpenedTime = models.DateTimeField(auto_now_add=True, auto_now=False)
    article_clicked = models.BooleanField(default=False)
    talkpage_clicked = models.BooleanField(default=False)
    post_clicked = models.BooleanField(default=False)
    tutorial_clicked = models.BooleanField(default=False)
    study_version = models.PositiveIntegerField(default=0)
    relevance_factor = models.BooleanField(default=False)
    likely_to_cite = models.BooleanField(default=False)
    may_include_reference = models.BooleanField(default=False)
    might_refer_to = models.BooleanField(default=False)
    relevant_to_research = models.BooleanField(default=False)
    within_area = models.BooleanField(default=False)
    on_expertise_topic = models.BooleanField(default=False)
    email1Count = models.PositiveIntegerField(default=0)
    email2Count = models.PositiveIntegerField(default=0)
    email3Count = models.PositiveIntegerField(default=0)
    especially_popular = models.BooleanField(default=False)
    highly_visible = models.BooleanField(default=False)
    highly_popular = models.BooleanField(default=False)
    private_first = models.BooleanField(default=False)
    econ_wikiproject_clicked = models.BooleanField(default=False)

    # auto_now_add=True means it will return the date and time when the user signedup, and auto_now means it will return the date and time when it's updated.
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    # Solves thge problem with latin and other characters.
    def __unicode__(self):
        return smart_unicode(self.name)

    class Meta:
        ordering = ('email',)

class Publication(models.Model):
    title = models.CharField(max_length=256, null=True, blank=True)
    citations = models.PositiveIntegerField(null=True, blank=True)
    publication_year = models.PositiveIntegerField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    fullcitation = models.CharField(max_length=1024, null=True, blank=True)

    # auto_now_add=True means it will return the date and time when the user signedup, and auto_now means it will return the date and time when it's updated.
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    # Solves thge problem with latin and other characters.
    def __unicode__(self):
        return smart_unicode(self.title)

    class Meta:
        ordering = ('title',)

class Publicationkeyword(models.Model):
    publication = models.ForeignKey('Publication')
    keyword = models.CharField(max_length=256, null=True, blank=True)

    # auto_now_add=True means it will return the date and time when the user signedup, and auto_now means it will return the date and time when it's updated.
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    # Solves thge problem with latin and other characters.
    def __unicode__(self):
        return smart_unicode(self.publication) + u' , ' + smart_unicode(self.keyword)

class Expertwikipub(models.Model):
    publication = models.ForeignKey('Publication')
    wikipage = models.ForeignKey('Wikipage')
    expert = models.ForeignKey('Expert')
    last_name_ocurances = models.PositiveIntegerField(null=True, blank=True)
    related_publications_number = models.PositiveIntegerField(null=True, blank=True)
    link_clicked = models.BooleanField(default=False)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    approved = models.BooleanField(default=False)
    submittedtotalkpage = models.BooleanField(default=False)
    approvedbywikipedians = models.BooleanField(default=False)
    rejectedbywikipedians = models.BooleanField(default=False)

    # auto_now_add=True means it will return the date and time when the user signedup, and auto_now means it will return the date and time when it's updated.
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    # Solves thge problem with latin and other characters.
    def __unicode__(self):
        return smart_unicode(self.expert) + u' , ' + smart_unicode(self.wikipage)

class Locationtimezone(models.Model):
    location = models.TextField(null=True, blank=True)
    timezone = models.TextField(null=True, blank=True)
    latitude = models.IntegerField(null=True, blank=True)
    longitude = models.IntegerField(null=True, blank=True)

    # auto_now_add=True means it will return the date and time when the user signedup, and auto_now means it will return the date and time when it's updated.
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    # Solves thge problem with latin and other characters.
    def __unicode__(self):
        return smart_unicode(self.location) + u': ' + smart_unicode(self.timezone)

class Expertkeywords(models.Model):
    expert = models.ForeignKey('Expert')
    keyword = models.TextField(null=True, blank=True)
    used = models.BooleanField(default=False)

    # auto_now_add=True means it will return the date and time when the user signedup, and auto_now means it will return the date and time when it's updated.
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    # Solves thge problem with latin and other characters.
    def __unicode__(self):
        return smart_unicode(self.expert)

class SimilarExpert(models.Model):
    expert = models.ForeignKey('Expert')
    relatedexpert = models.ForeignKey('Expert', related_name='related_expert_set')

    # auto_now_add=True means it will return the date and time when the user signedup, and auto_now means it will return the date and time when it's updated.
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    # Solves thge problem with latin and other characters.
    def __unicode__(self):
        return smart_unicode(self.expert)

    class Meta:
        ordering = ('expert',)

class Expertwikipubreferee(models.Model):
    expertwikipub = models.ForeignKey('Expertwikipub')
    firstname = models.CharField(max_length=256, null=True, blank=True)
    name = models.CharField(max_length=256, null=True, blank=True)
    school = models.CharField(max_length=256, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    specialization = models.CharField(max_length=256, null=True, blank=True)

    # auto_now_add=True means it will return the date and time when the user signedup, and auto_now means it will return the date and time when it's updated.
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    # Solves thge problem with latin and other characters.
    def __unicode__(self):
        return smart_unicode(self.name) + u' , ' + smart_unicode(self.email)

class StudyStatistic(models.Model):
    domain = models.CharField(max_length=256, null=True, blank=True)
    disciplinetotalnumphase1 = models.PositiveIntegerField(default=0)
    disciplinelinkclickednumphase1 = models.PositiveIntegerField(default=0)
    disciplineresponsenumphase1 = models.PositiveIntegerField(default=0)
    specialtytotalnumphase1 = models.PositiveIntegerField(default=0)
    specialtylinkclickednumphase1 = models.PositiveIntegerField(default=0)
    specialtyresponsenumphase1 = models.PositiveIntegerField(default=0)
    viewstotalnumphase1 = models.PositiveIntegerField(default=0)
    viewslinkclickednumphase1 = models.PositiveIntegerField(default=0)
    viewsresponsenumphase1 = models.PositiveIntegerField(default=0)
    citedpublicationtotalnumphase1 = models.PositiveIntegerField(default=0)
    citedpublicationlinkclickednumphase1 = models.PositiveIntegerField(default=0)
    citedpublicationresponsenumphase1 = models.PositiveIntegerField(default=0)
    grouptotalnumphase1 = models.PositiveIntegerField(default=0)
    grouplinkclickednumphase1 = models.PositiveIntegerField(default=0)
    groupresponsenumphase1 = models.PositiveIntegerField(default=0)
    disciplinetotalnumphase2 = models.PositiveIntegerField(default=0)
    disciplinelinkclickednumphase2 = models.PositiveIntegerField(default=0)
    disciplineresponsenumphase2 = models.PositiveIntegerField(default=0)
    specialtytotalnumphase2 = models.PositiveIntegerField(default=0)
    specialtylinkclickednumphase2 = models.PositiveIntegerField(default=0)
    specialtyresponsenumphase2 = models.PositiveIntegerField(default=0)
    viewstotalnumphase2 = models.PositiveIntegerField(default=0)
    viewslinkclickednumphase2 = models.PositiveIntegerField(default=0)
    viewsresponsenumphase2 = models.PositiveIntegerField(default=0)
    grouptotalnumphase2 = models.PositiveIntegerField(default=0)
    grouplinkclickednumphase2 = models.PositiveIntegerField(default=0)
    groupresponsenumphase2 = models.PositiveIntegerField(default=0)
    citedpublicationtotalnumphase2 = models.PositiveIntegerField(default=0)
    citedpublicationlinkclickednumphase2 = models.PositiveIntegerField(default=0)
    citedpublicationresponsenumphase2 = models.PositiveIntegerField(default=0)

    # auto_now_add=True means it will return the date and time when the user signedup, and auto_now means it will return the date and time when it's updated.
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    # Solves thge problem with latin and other characters.
    def __unicode__(self):
        return smart_unicode(self.domain)

# class ExpertPublication(models.Model):
#   expert = models.ForeignKey('Expert')
#   publication = models.ForeignKey('Publication')

#   # auto_now_add=True means it will return the date and time when the user signedup, and auto_now means it will return the date and time when it's updated.
#   timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
#   updated = models.DateTimeField(auto_now_add=False, auto_now=True)

#   # Solves thge problem with latin and other characters.
#   def __unicode__(self):
#       return smart_unicode(self.publication) + u' by ' + smart_unicode(self.expert)

# class ExpertWikiPagePublication(models.Model):
#   expert_wiki_page = models.ForeignKey('ExpertWikiPage')
#   publication = models.ForeignKey('Publication')

#   # auto_now_add=True means it will return the date and time when the user signedup, and auto_now means it will return the date and time when it's updated.
#   timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
#   updated = models.DateTimeField(auto_now_add=False, auto_now=True)

#   # Solves thge problem with latin and other characters.
#   def __unicode__(self):
#       return smart_unicode(self.publication) + u' , ' + smart_unicode(self.wiki_page)
