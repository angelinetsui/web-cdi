from django import forms
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div
from form_utils.forms import BetterModelForm
from django.core.urlresolvers import reverse




class AddStudyForm(BetterModelForm):
    name = forms.CharField(label='Study Name', max_length=51)
    instrument = forms.ModelChoiceField(queryset=instrument.objects.all(), empty_label="(choose from the list)")
    waiver = forms.CharField(widget=forms.Textarea, label='Waiver of Documentation text (no titles)', required = False)
    allow_payment = forms.BooleanField(required=False, label="Would you like to pay subjects in the form of Amazon gift cards? (You will need to upload gift card codes under \"Update Study\").")
    anon_collection = forms.BooleanField(required=False, label="Do you plan on collecting only anonymous data in this study? (e.g., posting ads on social media, mass emails, etc)")
    subject_cap = forms.IntegerField(label = "Maximum number of participants", required = False, min_value = 1, help_text = "Leave this blank if you do NOT want to limit the number of participants.", widget=forms.NumberInput(attrs={'placeholder': 'XXX participants'}))
    confirm_completion = forms.BooleanField(required = False, label="At the end of the form, would you like parents to confirm the age of their child and that they completed the entire test? (Best for anonymous data collections where you haven't personally vetted each participant)")
    allow_sharing = forms.BooleanField(required=False, label="Would you like participants to be able to share their Web-CDI results via Facebook?")

    def __init__(self, *args, **kwargs):
        super(AddStudyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'add-study'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('add_study')
        self.helper.layout = Layout(
            Field('name'),
            Field('instrument'),
            Field('waiver'),
            Field('allow_payment'),
            Field('anon_collection'),
            Field('subject_cap'),
            Field('confirm_completion'),
            Field('allow_sharing'),
        )
#        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = study
        exclude = ['study_group','researcher']

class AddPairedStudyForm(forms.Form):
    study_group = forms.CharField(label='Study Group Name', max_length=51)
    paired_studies = forms.MultipleChoiceField(choices = [])


    def __init__(self, *args, **kwargs):
        self.your_studies = kwargs.pop('your_studies', None)
        super(AddPairedStudyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'add-paired-study'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('add_paired_study')
        self.fields['paired_studies'].choices = self.your_studies
#        self.helper.add_input(Submit('submit', 'Submit'))

class RenameStudyForm(forms.Form):
    name = forms.CharField(label='Study Name', max_length=51, required=False)
    waiver = forms.CharField(widget=forms.Textarea, label='Waiver of Documentation', required=False)
    gift_codes = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Paste Amazon gift card codes here. Can be separated by spaces, commas, or new lines.'}), required=False, label='Gift Card Codes')
    gift_amount = forms.CharField(max_length=7, required=False, label="Amount per Card (in USD)", widget=forms.TextInput(attrs={'placeholder': '$XX.XX'}))

    def clean(self):
        cleaned_data = super(RenameStudyForm, self).clean()

    def __init__(self, old_study_name, *args, **kwargs):
        self.old_name = old_study_name
        self.old_waiver = kwargs.pop('study_waiver', None)
        self.old_gift_codes = None
        super(RenameStudyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'rename_study'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('rename_study', args=[old_study_name])
        # self.helper.form_action = '/interface/'+old_study_name+'rename_study/'
        self.fields['name'].initial = self.old_name
        self.fields['waiver'].initial = self.old_waiver
        self.helper.layout = Layout(
            Field('name'),
            Field('waiver'),
            Div(Field('gift_codes'), style="display: none;", css_class="gift_cards"),
            Div(Field('gift_amount'), css_class="gift_cards collapse"),
        )
