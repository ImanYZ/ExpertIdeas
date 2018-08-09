from django.conf.urls import patterns, include, url

from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'ExpertIdeas.views.emaillist', name='emaillist'),
    url(r'^(?i)JoinWikipedians', 'ExpertIdeas.views.studypage', name='studypage'),
    url(r'^(?i)SendEmail', 'ExpertIdeas.views.sendemail', name='sendemail'),
    url(r'^(?i)emailpreview', 'ExpertIdeas.views.emailpreview', name='emailpreview'),
    url(r'^(?i)posttotalkpage', 'ExpertIdeas.views.posttotalkpage', name='posttotalkpage'),
    url(r'^(?i)OptOut', 'ExpertIdeas.views.optout', name='optout'),
    url(r'^(?i)interested', 'ExpertIdeas.views.interested', name='interested'),
    url(r'^(?i)images.*', 'ExpertIdeas.views.images', name='images'),
    url(r'^(?i)wikipediaproxy', 'ExpertIdeas.views.wikipediaproxy', name='wikipediaproxy'),
    url(r'^(?i)redirectPage', 'ExpertIdeas.views.redirectPage', name='redirectPage'),
    url(r'^(?i)loadwikipages', 'ExpertIdeas.views.loadwikipages', name='loadwikipages'),
    url(r'^(?i)loadwikiarticlesCSV', 'ExpertIdeas.views.loadwikiarticlesCSV', name='loadwikiarticlesCSV'),
    url(r'^(?i)loadauthorpaperwikipages', 'ExpertIdeas.views.loadauthorpaperwikipages', name='loadauthorpaperwikipages'),
    url(r'^(?i)loadauthorpapers', 'ExpertIdeas.views.loadauthorpapers', name='loadauthorpapers'),
    url(r'^(?i)loadrepecauthors', 'ExpertIdeas.views.loadrepecauthors', name='loadrepecauthors'),
    url(r'^(?i)loadVerifiedRecommendations', 'ExpertIdeas.views.loadVerifiedRecommendations', name='loadVerifiedRecommendations'),
    url(r'^(?i)results', 'ExpertIdeas.views.results', name='results'),
    url(r'^(?i)csvrecommendations', 'ExpertIdeas.views.csvrecommendations', name='csvrecommendations'),
    url(r'^(?i)csvcomments', 'ExpertIdeas.views.csvcomments', name='csvcomments'),
    url(r'^(?i)csvresults', 'ExpertIdeas.views.csvresults', name='csvresults'),
    url(r'^(?i)csvdownload', 'ExpertIdeas.views.csvdownload', name='csvdownload'),
    url(r'^(?i)cleanDatabase', 'ExpertIdeas.views.cleanDatabase', name='cleanDatabase'),
    url(r'^(?i)setInappropriateComments', 'ExpertIdeas.views.setInappropriateComments', name='setInappropriateComments'),
    url(r'^(?i)removePilot1', 'ExpertIdeas.views.removePilot1', name='removePilot1'),
    url(r'^(?i)progressPage', 'ExpertIdeas.views.progressPage', name='progressPage'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^(?i)accounts/login/$', 'django.contrib.auth.views.login'),
	url(r'^(?i)accounts/logout/$', 'django.contrib.auth.views.logout'),
    url(r'^(?i)admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
    url(r'', 'ExpertIdeas.views.notfound', name='notfoundpage'),
)

# if settings.DEBUG:
# 	urlpatterns += static(settings.STATIC_URL,
# 		document_root=settings.STATIC_ROOT)
# 	urlpatterns += static(settings.MEDIA_URL,
# 		document_root=settings.MEDIA_ROOT)
