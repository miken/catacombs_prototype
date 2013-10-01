import os
import pandas as pd
import datetime

from django.test import TestCase
from django.core.files.storage import default_storage

from datacombo.models import Survey, ImportSession, CSVExport
from datacombo.upload import parse_csv_into_database, convert_raw_to_stack
from datacombo.export import s3_write_response_data
import datacombo.testdata


class DataExchangeIntegrityTest(TestCase):
    '''
    This will test the integrity of data in the system
    by comparing the output of an exported CSV file from Catacombs
    with an original CSV file used for upload

    For this test to work properly, you'll need to prepare 2 things:

        - Use `python manage.py dumpdata datacombo --indent=4 > datacombo/fixtures/datacombo_testdata.json` to dump database to a JSON file
            This file might be big! If you have response data in the json dump, delete them from the json to reduce test load time

        - Prepare sample CSV files (raw Qualtrics export) for testing in datacombo/testdata:
            + tch-ms.csv for MS Teacher Feedback
            + sch-hs.csv for HS Overall Experience

    '''
    fixtures = ['datacombo_testdata.json']

    def setUp(self):
        # Blank for now
        pass

    def create_session(self, survey, filetype):
        session = ImportSession()
        session.title = 'test'
        session.import_type = filetype
        session.date_created = datetime.datetime.now()
        session.survey = survey
        session.save()
        return session

    def create_csvexport(self, survey):
        # Create a CSVExport Session first
        export = CSVExport()
        export.title = 'Student Responses'
        export.export_type = 'response'
        now = datetime.datetime.now()
        export.date_requested = now
        export.survey = survey

        # Prepare CSV filename
        today = now.strftime('%Y%m%d')
        time = now.strftime('%H%M')
        filename = "integration_test_{surveycode}_responses_{today}_{time}.csv".format(
            surveycode=survey.code,
            today=today,
            time=time,
        )

        export.file_name = filename
        # Save export object first so it'll show up on the export management page
        export.save()
        return export

    def export_data(self, survey):
        export = self.create_csvexport(survey)
        # Turn debug on so we'll use web dyno directly
        s3_write_response_data(survey, export, debug=True)
        # Now return the export object, with url pointing to the right file
        return export

    def generate_data_integrity_test(self, filename, filetype):
        # Go to /testdata to retrieve the files needed
        os.chdir(datacombo.testdata.curr_dir)
        # Read original file into pandas
        orig = pd.read_csv(filename)
        orig = orig.dropna(subset=['V4'])
        surveycode = filename[:-4]
        survey = Survey.objects.get(code=surveycode)
        session = self.create_session(survey, filetype)

        # Now upload this file to database
        parse_csv_into_database(orig, filetype, survey, session, debug=True)
        surveycode = filename[:-4]
        survey = Survey.objects.get(code=surveycode)
        # Export data out
        export = self.export_data(survey)
        # Read from S3 URL
        from_s3 = pd.read_csv(export.url())

        # Now compare orig with from_s3
        # If survey is teacher feedback then convert it to stack first
        if survey.is_teacher_feedback():
            orig = convert_raw_to_stack(orig, survey)

        # DEBUG
        # Output two files for debugging
        orig.to_csv('orig.csv')
        from_s3.to_csv('from_s3.csv')

        # Compare lists of Qualtrics ID
        orig_qid_list = orig['V1'].tolist()
        orig_qid_list.sort()
        s3_qid_list = from_s3['Qualtrics ID'].tolist()
        s3_qid_list.sort()
        self.assertEqual(orig_qid_list, s3_qid_list)

        # Compare lists of PIN
        orig_pin_list = orig['V4'].tolist()
        orig_pin_list.sort()
        s3_pin_list = from_s3['PIN'].tolist()
        s3_pin_list.sort()
        self.assertEqual(orig_pin_list, s3_pin_list)

        # Delete file from S3 once done
        if default_storage.exists(export.file_name):
            default_storage.delete(export.file_name)
            print 'Deleted {} after testing.'.format(export.file_name)

    # Skipping this test
    # Reactivate it by deleting the word "skip_" in front of the method name
    def skip_test_integrity_tch_ms_raw(self):
        self.generate_data_integrity_test('tch-ms.csv', 'raw')

    # Skipping this test
    # Reactivate it by deleting the word "skip_" in front of the method name
    def test_integrity_sch_hs_raw(self):
        self.generate_data_integrity_test('sch-hs.csv', 'raw')
