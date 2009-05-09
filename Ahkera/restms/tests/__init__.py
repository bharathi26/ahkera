import os, shutil, sys
 
import coverage
from django.test.simple import run_tests as django_test_runner
 
from django.conf import settings

from domain import *
from feed import *
from join import *
from pipe import *
from message import *
from content import *

def test_runner_with_coverage(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    """Custom test runner.  Follows the django.test.simple.run_tests() interface."""
    # Start code coverage before anything else if necessary
    coverage_modules = []
    for module_name in settings.COVERAGE_MODULES:
        app_name = module_name.split(".")[0]
        if (not test_labels) or (app_name in test_labels):
            coverage_modules.append(__import__(module_name, globals(), locals(), ['']))
 
    if hasattr(settings, 'COVERAGE_MODULES'):
        coverage.use_cache(0) # Do not cache any of the coverage.py stuff
        coverage.start()
 
    test_results = django_test_runner(test_labels, verbosity, interactive, extra_tests)
 
    # Stop code coverage after tests have completed
    if hasattr(settings, 'COVERAGE_MODULES'):
        coverage.stop()
 
        # Print code metrics header
        print ''
        print '----------------------------------------------------------------------'
        print ' Unit Test Code Coverage Results'
        print '----------------------------------------------------------------------'
 
        coverage.report(coverage_modules, show_missing=1)
 
        # Print code metrics footer
        print '----------------------------------------------------------------------'
    else:
        print "No coverage modules defined in settings.py"
 
    return test_results

