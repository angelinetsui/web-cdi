import numpy, os.path

from django.shortcuts import render, redirect
from django.views.generic import UpdateView
from django.http import Http404
from django.utils import timezone

# simulation package contains the Simulator and all abstract classes
from catsim.simulation import *
# initialization package contains different initial proficiency estimation strategies
from catsim.initialization import *
# selection package contains different item selection strategies
from catsim.selection import *
# estimation package contains different proficiency estimation methods
from catsim.estimation import *
# stopping package contains different stopping criteria for the CAT
from catsim.stopping import *
from .stopper import CustomStopper

from cdi_forms.models import requests_log, BackgroundInfo

from cdi_forms.views import BackgroundInfoView, CreateBackgroundInfoView, BackpageBackgroundInfoView, PROJECT_ROOT
from researcher_UI.models import administration

from .forms import CatItemForm
from .models import InstrumentItem, CatResponse
from .utils import string_bool_coerce

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
        try:
            items = InstrumentItem.objects.filter(id__in=self.object.catresponse.administered_items)
        except: items = None
        if items :
            hardest = items.order_by('-difficulty')[0].definition
            easiest = items.order_by('difficulty')[0].definition
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

    def get_items(self):
        self.instrument_items = InstrumentItem.objects.filter(instrument=self.object.study.instrument)
        items = []
        for instrument_item in self.instrument_items:
            items.append([instrument_item.discrimination, instrument_item.difficulty, instrument_item.guessing, instrument_item.upper_asymptote])
        
        return numpy.asarray(items, dtype=numpy.float32)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'btn-back' in request.POST:
            return redirect('cat_forms:background-info', pk=self.object.backgroundinfo.id)

        administered_responses = self.object.catresponse.administered_responses or []
        administered_words = self.object.catresponse.administered_words or []
        administered_items = self.object.catresponse.administered_items or []
        
        instrument_item = InstrumentItem.objects.get(id=int(self.request.POST['word']))
        administered_words.append(instrument_item.definition)
        if 'yes' in self.request.POST:
            administered_responses.append(True)
        else:
            administered_responses.append(False)

        items = self.get_items()
        for index, item in enumerate(self.instrument_items):
            if item == instrument_item:
                administered_items.append(index)
                break

        estimator = HillClimbingEstimator()
        new_theta = estimator.estimate(items=items, administered_items=administered_items, response_vector=administered_responses, est_theta=self.object.catresponse.est_theta)

        self.object.catresponse.administered_responses=administered_responses
        self.object.catresponse.administered_items=administered_items
        self.object.catresponse.administered_words = administered_words
        self.object.catresponse.est_theta = new_theta

        stopper = CustomStopper(self.min_words, self.max_words, self.min_error)
        if stopper.stop(administered_items=items[administered_items], theta=self.object.catresponse.est_theta):
            filename = os.path.realpath(PROJECT_ROOT + '/form_data/background_info/' + self.object.study.instrument.name + '.json')
            print(filename)
            if  os.path.isfile(filename):
                self.object.completedSurvey = True
            else :
                self.object.completed = True
            self.object.save()

        self.object.catresponse.save()

        self.request.METHOD = 'GET'
        return redirect('cat_forms:administer_cat_form', hash_id=self.hash_id)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        ctx['form'] = CatItemForm(context={'word':self.word}, initial={'word':self.word})
        try:
            if '*' in self.word.definition: ctx['footnote'] = True
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

        items = self.get_items()

        initializer = RandomInitializer()
        selector = MaxInfoSelector()
        self.est_theta = initializer.initialize()

        cat_response, created = CatResponse.objects.get_or_create(administration=self.object)
        if created or not cat_response.est_theta:
            cat_response.est_theta = self.est_theta
            cat_response.save()

        administered_responses = self.object.catresponse.administered_responses or []
        administered_items = self.object.catresponse.administered_items or []
        administered_words = self.object.catresponse.administered_words or []
        self.est_theta = self.object.catresponse.est_theta

        item_index = selector.select(items=items, administered_items=administered_items, est_theta=self.est_theta)

        self.word = self.instrument_items[int(item_index)]

        return super().get(request, *args, **kwargs) 
