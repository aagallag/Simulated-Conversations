# Simulated Conversation Models
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.files import File
import datetime
from tinymce.models import HTMLField  # tinymce for rich text embeds

####remember to uncomment foreign key entries as models are added####
class Conversation(models.Model):
        templateID      = models.ForeignKey('Template')
        researcherID    = models.ForeignKey(User)
        studentName     = models.CharField(max_length=50)
        studentEmail    = models.EmailField(max_length=254)
        dateTime        = models.DateTimeField(auto_now_add=True)
        typedResponse   = models.NullBooleanField(default=False, null=True)  # Conversation ended with a typed response

        def __unicode__(self):
                return u" %s: %s" % (str(self.dateTime), self.studentName)

class Response(models.Model):
        pageInstanceID  = models.ForeignKey('PageInstance') 
        conversationID  = models.ForeignKey(Conversation)
        order           = models.SmallIntegerField()
        choice          = models.ForeignKey('TemplateResponseRel') # needs to default to a certain flag so can be nullable, in case of recorded audio with no choice
        audioFile       = models.FileField(upload_to='audio')
        typedResponse   = models.CharField(max_length=100, null=True) # this holds an optional typed response
#       audioFile is tied to MEDIA_ROOT set in settings, to save in a
#       subdirectory within MEDIA_ROOT, set upload_to=$PATH.  
#       To do the madia management manually change this to assume ( FilePathField );
        def __unicode__(self):
                return u"%d: %s" % (self.order, self.choice)


#The validationKey must be unique to allow the Student Login page to look up the templateID by validation key
class StudentAccess(models.Model):
    studentAccessID = models.AutoField(primary_key=True)
    templateID = models.ForeignKey('Template')
    researcherID = models.ForeignKey(User)
    validationKey = models.CharField(max_length = 50, unique=True)
    expirationDate = models.DateField()
    collectEmail = models.BooleanField(default = False) # collect email on this link?
    playbackAudio = models.BooleanField(default = False) # can the student playback the audio in line
    playbackVideo = models.BooleanField(default = False) # can the student playback the video?
    allowTypedResponse = models.BooleanField(default = False)  # can a student go off script and type their own response?
    
    def __unicode__(self):
        return u'%s %s %s %s %s' % \
            (self.studentAccessID, self.templateID, 
             self.researcherID, self.validationKey, 
             self.expirationDate)

    # Returns a url for the student login page with the passed 'key'.
    def get_link(self, key):
        student_site = reverse('StudentLogin',args=[key])
        return student_site

    #Returns a url for the student login page without a key passed.
    def get_base_link(self):
        student_site = "/student/"
        return settings.SITE_ID + student_site

#Templates: a list of templates and who they belong to. The firstInstanceID points to a 
#templateFlowRelID which is the first video in the template. Deleted refers to if a template was deleted.
#Version refers to template version
class Template(models.Model):
    templateID      = models.AutoField(primary_key = True)
    researcherID    = models.ForeignKey(User)
    firstInstanceID = models.ForeignKey("PageInstance", blank=True, null=True)
    shortDesc       = models.TextField()
    deleted         = models.BooleanField(default = False)   # whether or not this template has been deleted
    version         = models.IntegerField(default = 1)    # particular version of this template, base 1
    
    def __unicode__(self):
        if self.version > 1:
            return u"%s Version: %d" % (self.shortDesc, self.version)
        else:
            return u"%s" % self.shortDesc
            
#PageInstance: this relates videos or responses to a template. The template is referenced by
#templateID and researcherID. videoOrResponse tells you whether it's a VIDEO INSTANCE or a 
#RESPONSE INSTANCE, by literally video or response. If its a video, it will have a videoLink 
#and richText, with enablePlayback as a boolean that can enable or disable the video playback buttons. 
#If it's a response instance, these values will be blank.
class PageInstance(models.Model):
    pageInstanceID  = models.AutoField(primary_key = True)
    templateID      = models.ForeignKey(Template, blank=True, null=True)
    videoOrResponse = models.CharField(max_length = 8, default = "response") #considering omitting this and just using videoLink to determine variety...
    videoLink       = models.CharField(max_length = 11, null = True)  # this will store the alphanumberic code of a url such as: http://img.youtube.com/vi/zJ8Vfx4721M
    #richText        = models.TextField()    # NOTE:  this has to store raw html
    richText        = HTMLField() # rich text field
    enablePlayback  = models.BooleanField(default = True)
    
    def __unicode__(self):
        if self.videoOrResponse == "video":  # consider change this to query videoLink not null?
            return u"Video instance"
        else:
            return u"Response instance"

    def get_pageInstanceID(self):
        return self.pageInstanceID



# Note(Daniel): Implemented the SharedResponse class per the design spec.
class SharedResponses(models.Model):
    sharedResponseID = models.AutoField(primary_key=True)
    responseID = models.ForeignKey('Conversation')
    researcherID = models.ForeignKey(User)
    dateTimeShared = models.DateTimeField(auto_now=True)
    #typedResponse = models.

    # Note(Daniel): To insure that a response is only shared once
    # with a researcher, I used the unique_together to force this 
    # requirement on the responseID and researcherID
    # Note - This requirement was not specified in the design spec.
    class Meta:
        unique_together = ("responseID", "researcherID")

#TemplateResponseRel: this relates the several possible responses to one pageInstanceID, ordered by 
# optionNumber. If the pageInstance is a response, the next page instance will be referenced here.
class TemplateResponseRel(models.Model):
    templateResponseRelID = models.AutoField(primary_key = True)
    templateID            = models.ForeignKey(Template)
    pageInstanceID        = models.ForeignKey(PageInstance, related_name='templateresponserel_page') # id of dummy page
    responseText          = models.TextField()
    optionNumber          = models.IntegerField(default = 1)
    nextPageInstanceID    = models.ForeignKey(PageInstance, blank=True, null=True, related_name='templateresponserel_nextpage' )
    
    def __unicode__(self):
        return u"Template response relation for template: %s" % self.templateID.shortDesc

#TemplateFlowRel: this determines how the template will flow. A template is referenced by
# templateID and researcherID. The first page in the flow will be determined by the 
# Templates table, and each page after that can be looked up by referencing pageInstanceID
# and the corresponding nextPageInstanceID, but only if it's a video. If it's a response,
# you need to look up the nextPageInstanceID based on which optionNumber it is in the TemplateReponseRel table.
class TemplateFlowRel(models.Model):
    templateFlowRelID  = models.AutoField(primary_key = True)
    templateID         = models.ForeignKey(Template, blank=True, null=True)
    pageInstanceID     = models.ForeignKey(PageInstance, blank=True, null=True, related_name='templateflowrel_page')
    nextPageInstanceID = models.ForeignKey(PageInstance, default=None, blank=True, null=True, related_name='templateflowrel_nextpage')
      
    def __unicode__(self):
        return u"Template flow relation for template: %s" % self.templateID.shortDesc

    def curr_page(self):
        return self.pageInstanceID

    def nex_page(self):
        return self.nextPageInstanceIDtemplateID 

#TemplateInProgress: this allows the researcher to save a template
# in progress. there is no error checking before saving, and the researcher
# can come back to it before saving as a template.
class TemplateInProgress(models.Model):
    templateInProgressID    = models.AutoField(primary_key = True)
    researcherID            = models.ForeignKey(User)
    conversationTitle       = models.TextField()
    videoList               = models.TextField()
    responseTextList        = models.TextField()
    responseParentVideoList = models.TextField()
    responseChildVideoList  = models.TextField()
    dateTimeSaved           = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"A saved template in progress"

class TemplateInProgressRichText(models.Model):
    TIPRTID                 = models.AutoField(primary_key = True)
    templateInProgressID    = models.ForeignKey(TemplateInProgress, blank=True, null=True)
    video                   = models.TextField()
    richText                = HTMLField()
