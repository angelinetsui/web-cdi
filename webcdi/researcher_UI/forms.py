from django import forms
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class AddStudyForm(forms.Form):
    name = forms.CharField(label='Study Name', max_length=51)
    instrument = forms.ModelChoiceField(queryset=instrument.objects.all(), empty_label="(choose from the list)")
    waiver = forms.CharField(widget=forms.Textarea, label='Waiver of Documentation text (no titles)', required = False)


    def __init__(self, *args, **kwargs):
        super(AddStudyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'add-study'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.form_method = 'post'
        self.helper.form_action = '/interface/add_study/'
#        self.helper.add_input(Submit('submit', 'Submit'))

class AddPairedStudyForm(forms.Form):
    study_group = forms.CharField(label='Study Group Name', max_length=51)
    paired_studies = forms.MultipleChoiceField(choices = [])


    def __init__(self, *args, **kwargs):
        super(AddPairedStudyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'add-paired-study'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.form_method = 'post'
        self.helper.form_action = '/interface/add_paired_study/'
        self.fields['paired_studies'].choices = study.objects.filter(study_group = "").values_list("name","name")
#        self.helper.add_input(Submit('submit', 'Submit'))

class RenameStudyForm(forms.Form):
    name = forms.CharField(label='Study Name', max_length=51)
    waiver = forms.CharField(widget=forms.Textarea, label='Waiver of Documentation', required = False)


    def __init__(self, old_study_name, *args, **kwargs):
        super(RenameStudyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'rename_study'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.form_method = 'post'
        self.helper.form_action = '/interface/'+old_study_name+'rename_study/'
#        self.helper.add_input(Submit('submit', 'Submit'))
