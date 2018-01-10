from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator,MinValueValidator


# Model for individual instruments
class instrument(models.Model):
    name = models.CharField(max_length = 51, primary_key=True) # Instrument short name
    verbose_name = models.CharField(max_length = 51, blank = True) # Instrument official title
    language = models.CharField(max_length = 51) # Instrument's language. For 'English Words & Sentences' this would be 'English'
    form = models.CharField(max_length = 51) # Instrument's form type abbreviation. For 'English Words & Sentences' this would be 'WS'
    min_age = models.IntegerField(verbose_name = "Minimum age") # Minimum age in months that instrument was built for
    max_age = models.IntegerField(verbose_name = "Maximum age") # Maximum age in months that instrument was built for
    def __str__(self):
        return self.verbose_name
    class Meta:
         unique_together = ('language', 'form') # Each instrument in the database must have a unique combination of language and form type
    

# Model for individual studies
class study(models.Model):
    researcher = models.ForeignKey("auth.user") # Researcher's name
    name = models.CharField(max_length = 51) # Study name
    instrument = models.ForeignKey("instrument") # Instrument associated with study
    waiver = models.TextField(blank = True) # IRB Waiver of documentation for study or any additional instructions provided to participant
    study_group = models.CharField(max_length = 51, blank = True) # Study group
    anon_collection = models.BooleanField(default=False) # Whether participants in study will all be anonymous
    subject_cap = models.IntegerField(blank = True, null=True) # Subject cap to limit number of completed administrations
    confirm_completion = models.BooleanField(default=False) # Whether to have participant confirm child's age and that test was completed to best of ability at end of study
    allow_payment = models.BooleanField(default=False) # Whether to reward participants with gift card codes upon completion
    allow_sharing = models.BooleanField(default=False) # Whether to allow participants to share results via Facebook
    test_period = models.IntegerField(default=14, validators = [MinValueValidator(1), MaxValueValidator(14)]) # Number of days after test creation that a participant may work on and complete administration  
    prefilled_data = models.IntegerField(default=0)
    min_age = models.IntegerField(verbose_name = "Minimum age", blank = True, null=True) # Minimum age in months for study
    max_age = models.IntegerField(verbose_name = "Maximum age", blank = True, null=True) # Maximum age in months for study
    birth_weight_units = models.CharField(max_length = 5, default="lb")

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('researcher', 'name') # Each study in database must have a unique combination of researcher and name
    
def get_meta_header(): # Returns a list of variables for administration objects
    return ['study', 'subject_id', 'administration_number', 'link', 'completed', 'completedBackgroundInfo', 'expiration_date', 'last_modified']

def get_background_header(): # Returns a list of variables for backgroundinfo objects
    return ['id', 'age', 'sex', 'birth_order', 'birth_weight_lb', 'birth_weight_kg', 'early_or_late', 'due_date_diff', 'mother_yob', 'mother_education', 'father_yob', 'father_education', 'annual_income', 'child_hispanic_latino', 'caregiver_info', 'other_languages_boolean', 'language_from', 'language_days_per_week', 'language_hours_per_day', 'ear_infections_boolean', 'ear_infections', 'hearing_loss_boolean', 'hearing_loss', 'vision_problems_boolean', 'vision_problems']

# Model for individual administrations
class administration(models.Model):
    study = models.ForeignKey("study") # Study name
    subject_id = models.IntegerField() # Subject ID, unique to the associated study
    repeat_num = models.IntegerField(verbose_name = "Administration number") # Ordinal number of tests given to this particular subject ID. For example, if this is Subject 30's third test, this field will have '3' stored
    url_hash = models.CharField(max_length=128, unique=True) # Associated URL hash
    completed = models.BooleanField() # Whether administration has been marked as completed
    completedBackgroundInfo = models.BooleanField(default=False) # Whether backgroundinfo has been completed
    due_date = models.DateTimeField(verbose_name = "Expiration date") # Expiration date for administration
    last_modified = models.DateTimeField(auto_now = True) # Date when the administration object was last updated
    created_date = models.DateTimeField(verbose_name = "Creation date", auto_now_add = True) # Date administration object was created
    page_number = models.IntegerField(verbose_name = "Page number", default = 0) # Current progress for CDI form
    analysis = models.NullBooleanField(verbose_name = "Confirmed Age and Completion", default = None) # Whether participant confirmed child's age and that form was completed to best of ability
    bypass = models.NullBooleanField(verbose_name = "Willing to forgo payment", default = None) # Whether participant explicitly bypassed overflow page if study has reached subject cap
    include = models.NullBooleanField(verbose_name = "Include for eventual analysis", default = True) # Field for marking if a researcher wants to include data in study. Currently not used.

    class Meta:
        unique_together = ('study', 'subject_id', 'repeat_num') # Each administration object has a unique combination of study ID, subject ID, and administration number. They also have a unique hash ID identifier but uniqueness of hash ID is not enforced due to odds of 2 participants having the same hash ID being cosmically low.

    def get_meta_data(self):
        return [self.study, self.subject_id, self.repeat_num, self.url_hash, self.completed, self.completedBackgroundInfo, self.due_date, self.last_modified]

# Model for item responses within an administration
class administration_data(models.Model):
    administration = models.ForeignKey("administration") # Associated administration
    item_ID = models.CharField(max_length = 101) # ID associated for each CDI item
    value = models.CharField(max_length=200) # Response given by participant to this particular item
    class Meta:
        unique_together = ('administration', 'item_ID') # Each administation_data object must have a unique combination of administration ID and item ID.

# Model for stored gift card codes
class payment_code(models.Model):
    study = models.ForeignKey("study") # Associated study name
    hash_id = models.CharField(max_length=128, unique=True, null=True) # Populated with hash ID of participant that code was given to. Null until code is rewarded. Uniqueness is enforced (one administration can only have 1 code)
    added_date = models.DateTimeField(verbose_name = "Date code was added to database", auto_now_add = True) # Date that payment code was first added to database
    assignment_date = models.DateTimeField(verbose_name = "Date code was given to participant", null=True) # Date that payment code was given to a participant
    payment_type = models.CharField(max_length=50) # Type of gift card code. Currently only 'Amazon' is allowed
    gift_amount = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Monetary value") # Monetary amount associated with gift card code
    gift_code = models.CharField(max_length=50) # Gift card code

    class Meta:
        unique_together = ('payment_type', 'gift_code') # Each object must have a unique combination of code type and the actual gift card code itself

# Model for stored IP addresses (only stored for studies created by 'langcoglab' and specific studies marked to log IP addresses, under Stanford's IRB approval)
class ip_address(models.Model):
    study = models.ForeignKey("study") # Study associated with IP address
    ip_address = models.CharField(max_length = 30) # Actual IP address
    date_added = models.DateTimeField(verbose_name = "Date IP address was added to database", auto_now_add = True) # Date that IP address was added to database.
