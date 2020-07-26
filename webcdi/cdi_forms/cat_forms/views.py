import os.path

from django.shortcuts import render, redirect
from django.views.generic import UpdateView
from django.http import Http404
from django.utils import timezone
from django.db.models import Min

from cdi_forms.models import requests_log, BackgroundInfo

from cdi_forms.views import BackgroundInfoView, CreateBackgroundInfoView, BackpageBackgroundInfoView, PROJECT_ROOT
from researcher_UI.models import administration

from .forms import CatItemForm
from .models import CatResponse
from .utils import string_bool_coerce
from .cdi_cat_api import cdi_cat_api

# Create your views here.

class CATBackgroundInfoView(BackgroundInfoView):
    pass

class CATCreateBackgroundInfoView(CreateBackgroundInfoView):
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CATBackpageBackgroundInfoView(BackpageBackgroundInfoView):
    pass

class AdministerAdministraionView(UpdateView):
    model = administration
    refresh = False
    hash_id = None
    form_class = CatItemForm
    template_name = 'cdi_forms/cat_forms/cat_form.html'
    word=None
    instrument_items = None
    max_words = 50
    min_words = 20
    min_error = 0.15
    est_theta = None

    def get_hardest_easiest(self):
        if self.object.catresponse.administered_items :
            hardest = cdi_cat_api(f'hardestWord?items={self.object.catresponse.administered_items}')['definition']
            easiest = cdi_cat_api(f'easiestWord?items={self.object.catresponse.administered_items}')['definition']
        else : 
            hardest = None
            easiest = None
        return hardest, easiest

    def get_object(self, queryset=None):
        try:
            self.hash_id = self.kwargs['hash_id']
            obj = administration.objects.get(url_hash=self.hash_id)
        except:
            raise Http404("Administration not found")
        return obj

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'btn-back' in request.POST:
            return redirect('cat_forms:background-info', pk=self.object.backgroundinfo.id)

        administered_responses = self.object.catresponse.administered_responses or []
        administered_words = self.object.catresponse.administered_words or []
        administered_items = self.object.catresponse.administered_items or []
        
        self.word = {'index': self.request.POST['word_id'], 'definition' : self.request.POST['label']}
        
        administered_words.append(self.word['definition'])
        if 'yes' in self.request.POST:
            administered_responses.append(True)
        else:
            administered_responses.append(False)

        administered_items.append(self.word['index'])
        
        self.object.catresponse.administered_responses = administered_responses
        self.object.catresponse.administered_items = administered_items
        self.object.catresponse.administered_words = administered_words
        self.object.catresponse.save()

        if len(administered_items) > 49 :
            filename = os.path.realpath(PROJECT_ROOT + '/form_data/background_info/' + self.object.study.instrument.name + '.json')
            if  os.path.isfile(filename):
                self.object.completedSurvey = True
            else :
                self.object.completed = True
            self.object.save()

        self.request.METHOD = 'GET'
        return redirect('cat_forms:administer_cat_form', hash_id=self.hash_id)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        if self.word: 
            ctx['form'] = CatItemForm(context={'label':self.word['definition']}, initial={'word_id':self.word['index'], 'label':self.word['definition']})
            try:
                if '*' in self.word['definition']: ctx['footnote'] = True
            except AttributeError:
                pass

        ctx['max_words'] = self.max_words
        if self.object.catresponse.administered_words:
            ctx['words_shown'] = len(self.object.catresponse.administered_words) + 1
        else:
            ctx['words_shown'] = 1

        ctx['est_theta'] = self.est_theta
        ctx['due_date'] = self.object.due_date.strftime('%b %d, %Y, %I:%M %p')
        ctx['hardest'], ctx['easiest'] = self.get_hardest_easiest()
        return ctx

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        requests_log.objects.create(url_hash=self.hash_id, request_type="GET")
        if self.object.completed or self.object.due_date < timezone.now():
            return render(request, 'cdi_forms/cat_forms/cat_completed.html', context=self.get_context_data())
        background_instance, created = BackgroundInfo.objects.get_or_create(administration=self.object) 
        if self.object.completedSurvey:
            return redirect('backpage-background-info', pk=background_instance.pk)
        elif not self.object.completedBackgroundInfo:
            return redirect('background-info', pk=background_instance.pk)

        cat_response, created = CatResponse.objects.get_or_create(administration=self.object)
        if created or not cat_response.est_theta:
            cat_response.est_theta = self.est_theta
            cat_response.save()

        administered_responses = self.object.catresponse.administered_responses or []
        administered_items = self.object.catresponse.administered_items or []
        administered_words = self.object.catresponse.administered_words or []
        self.est_theta = self.object.catresponse.est_theta

        
        if len(administered_words) < 1 : # first word might be specified by age
            self.word = cdi_cat_api(f'startItem?age_mos={self.object.backgroundinfo.age}')
        else:    
            self.word = cdi_cat_api(f'nextItem?responses={list(map(int,administered_responses))}&items={administered_items}')
            if self.word == 'stop':
                filename = os.path.realpath(PROJECT_ROOT + '/form_data/background_info/' + self.object.study.instrument.name + '.json')
                if  os.path.isfile(filename):
                    self.object.completedSurvey = True
                else :
                    self.object.completed = True
                self.object.save()
                return redirect('cat_forms:administer_cat_form', hash_id=self.hash_id)
            else :
                self.object.catresponse.est_theta = self.word['curTheta']
                self.object.save()
        
        return super().get(request, *args, **kwargs) 
