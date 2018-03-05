import json
import re
from django.core.management.base import BaseCommand
from cdi_forms.models import *
from researcher_UI.models import *
import csv
from django.apps import apps


# Populates the ItemInfo and ItemMap models with data from instrument definition files.
# Given no arguments, does so for all instruments in 'static/json/instruments.json'.
# Given a language with -l and a form with -f, does so for only their Instrument object.

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]
        
class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-l', '--language', type=str)
        parser.add_argument('-f', '--form', type=str)

    def handle(self, *args, **options):

        instruments = json.load(open('static/json/instruments.json'))

        if options['language'] and options['form']:
            input_language, input_form = options['language'], options['form']
            input_instruments = filter(lambda instrument: instrument['language'] == input_language and
                                                          instrument['form'] == input_form,
                                       instruments)
        elif options['language'] and not options['form']:
            input_language = options['language']
            input_instruments = filter(lambda instrument: instrument['language'] == input_language,
                                       instruments)
        elif not options['language'] and options['form']:
            input_form = options['form']
            input_instruments = filter(lambda instrument: instrument['form'] == input_form,
                                       instruments)
        else:
            input_instruments = instruments

        for curr_instrument in input_instruments:

            instrument_language, instrument_form = curr_instrument['language'], curr_instrument['form']

            instrument_obj = instrument.objects.get(form=instrument_form, language=instrument_language)
            instrument_model = apps.get_model(app_label='cdi_forms', model_name=instrument_obj.name)

            print "    Populating items for", instrument_language, instrument_form

            ftype = curr_instrument['csv_file'].split('.')[-1]

            if ftype == 'csv':

                contents = list(unicode_csv_reader(open(curr_instrument['csv_file'])))
                col_names = contents[0]
                nrows = len(contents)
                get_row = lambda row: contents[row]
            else:
                raise IOError("Instrument file must be a CSV.")

            for row in xrange(1, nrows):
                row_values = get_row(row)
                if len(row_values) > 1:
                    itemID = row_values[col_names.index('itemID')]
                    item = row_values[col_names.index('item')]
                    item_type = row_values[col_names.index('item_type')]
                    item_category = row_values[col_names.index('category')]
                    item_choices = row_values[col_names.index('choices')]
                    choices_key = None
                    if item_type not in ['combination_examples']:
                        try:
                            choices_key = Choices.objects.get(choice_set_en = item_choices)
                        except:
                            raise IOError("Can't find choice set %s in model for %s" % (item_category, itemID, ))

                    definition = row_values[col_names.index('definition')]
                    gloss = row_values[col_names.index('gloss')]
                    if 'complexity_category' in col_names:
                        complexity_category = row_values[col_names.index('complexity_category')]
                    else:
                        complexity_category = None

                    if 'uni_lemma' in col_names:
                        uni_lemma = row_values[col_names.index('uni_lemma')]
                    else:
                        uni_lemma = None

                    data_dict = {'item': item,
                                 'item_type': item_type,
                                 'category': item_category,
                                 'choices': choices_key,
                                 'definition': definition,
                                 'gloss': gloss,
                                 'complexity_category': complexity_category,
                                 'uni_lemma': uni_lemma}

                    cdi_item, created = instrument_model.objects.update_or_create(itemID = itemID, defaults=data_dict,)

