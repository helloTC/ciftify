#!/usr/bin/env python3
# functional tests for the run.py script
# note: to start we will just run many dry-runs to insure that the correct
#      command-line calls are generated given the user args..

# also note! pybids has three test datasets! we can use!
# note all the data has been removed from the nifti files to make them fit in github so running them fully won't work..
# but ds005 we could get through datalad..
# also note: ds00005 does have an ok res T2 so it may be worth testing against the HCPPipelines..
# but no public fmriprep derivatives..
import os
import unittest
import copy
from bids.tests import get_test_data_path
from mock import patch
import importlib
from docopt import docopt
import ciftify.bidsapp.run as run_script
import pprint

def mock_run_side_effect(cmd, dryrun=False,
        suppress_stdout=False,
        suppress_echo = False,
        suppress_stderr = False,
        env = None):
    '''just returns the command as a string'''
    if type(cmd) is list:
        cmd = ' '.join(cmd)
    return cmd

def simple_main_run(user_args_list):
    '''the code from the main function minus the logging bits'''
    print(user_args_list)
    docstring = run_script.__doc__
    arguments = docopt(docstring, user_args_list)
    settings = run_script.Settings(arguments)
    print(settings.__dict__)
    if settings.analysis_level == "group":
        ret = run_script.run_group_workflow(settings)
    if settings.analysis_level == "participant":
        ret = run_script.run_participant_workflow(settings)
    return ret

ds005_bids = os.path.join(get_test_data_path(), 'ds005')
ds7t_bids = os.path.join(get_test_data_path(), '7t_trt')
synth_bids = os.path.join(get_test_data_path(), 'synthetic')


def parse_call_list_into_strings(call_list):
    '''take the call list and parse into a normal list'''
    cmd_list = []
    for i in call_list:
        cmd = i[0][0]
        if type(cmd) is list:
            cmd = ' '.join(cmd)
        cmd_list.append(cmd)
    return(cmd_list)

def count_calls_to(utility_name, call_list, call_contains = None):
    '''count the number of calls to a specific function with or without args'''
    count = 0
    for cmd in call_list:
        if cmd.startswith(utility_name):
            if call_contains != None:
                 if call_contains in cmd:
                        count += 1
            else:
                count += 1
    return(count)


@patch('ciftify.bidsapp.run.run', side_effect = mock_run_side_effect)
def test_default_all_participants_for_ds005(mock_run):

    uargs = [ds005_bids, '/output/dir', 'participant']
    ret = simple_main_run(uargs)
    call_list = parse_call_list_into_strings(mock_run.call_args_list)
    assert count_calls_to('fmriprep', call_list) > 0
    # assert count_calls_to('fmriprep', call_list) == 0
    # assert count_calls_to('ciftify_recon_all', call_list) == 0
    # assert count_calls_to('ciftify_subject_fmri', call_list) == 0


@patch('ciftify.bidsapp.run.run')
def test_default_one_participant_for_ds005(mock_run):

    uargs1 = [ds005_bids, '/output/dir', 'participant', '--participant_label=14']
    ret = simple_main_run(uargs1)
    call_list = parse_call_list_into_strings(mock_run.call_args_list)
    assert count_calls_to('fmriprep', call_list) > 0
    # assert count_calls_to('fmriprep', call_list) == 4
    # assert count_calls_to('ciftify_recon_all', call_list) == 1
    # assert count_calls_to('ciftify_subject_fmri', call_list) == 3
    # assert count_calls_to('ciftify_subject_fmri', call_list, call_contains = 'sub-01') == 0



@patch('ciftify.bidsapp.run.run')
def test_default_two_participants_for_ds005(mock_run):

    uargs = [ds005_bids, '/output/dir', 'participant', '--participant_label=01,14']
    ret = simple_main_run(uargs)
    call_list = parse_call_list_into_strings(mock_run.call_args_list)
    # assert count_calls_to('fmriprep', call_list) == 8
    # assert count_calls_to('ciftify_recon_all', call_list) == 2
    # assert count_calls_to('ciftify_subject_fmri', call_list) == 6
    # assert count_calls_to('ciftify_subject_fmri', call_list, call_contains = 'sub-01') == 0



@patch('ciftify.bidsapp.run.run')
def test_default_one_participant_anat_for_ds005(mock_run):

    uargs = [ds005_bids, '/output/dir', 'participant', '--participant_label=14', '--anat-only']
    ret = simple_main_run(uargs)
    call_list = parse_call_list_into_strings(mock_run.call_args_list)
    # assert count_calls_to('fmriprep', call_list, call_contains = "--participant_label 14") == 1
    # assert count_calls_to('ciftify_recon_all', call_list) == 1
    # assert count_calls_to('ciftify_subject_fmri', call_list) == 0

@patch('ciftify.bidsapp.run.run')
def test_default_all_participants_for_synth(mock_run):

    uargs = [synth_bids, '/output/dir', 'participant']
    ret = simple_main_run(uargs)
    call_list = parse_call_list_into_strings(mock_run.call_args_list)
    # assert count_calls_to('fmriprep', call_list) == 0
    # assert count_calls_to('ciftify_recon_all', call_list) == 0
    # assert count_calls_to('ciftify_subject_fmri', call_list) == 0

@patch('ciftify.bidsapp.run.run')
def test_default_one_subject_rest_for_synth(mock_run):

    uargs = [synth_bids, '/output/dir', 'participant', '--participant_label=02', '--task_label=rest']
    ret = simple_main_run(uargs)
    call_list = parse_call_list_into_strings(mock_run.call_args_list)
    # assert count_calls_to('fmriprep', call_list) == 0
    # assert count_calls_to('ciftify_recon_all', call_list) == 0
    # assert count_calls_to('ciftify_subject_fmri', call_list) == 0

@patch('ciftify.bidsapp.run.run')
def test_default_one_subject_one_session_for_synth(mock_run):


    uargs = [synth_bids, '/output/dir', 'participant', '--participant_label=02', '--session_label=01']
    ret = simple_main_run(uargs)
    call_list = parse_call_list_into_strings(mock_run.call_args_list)
    # assert count_calls_to('fmriprep', call_list, call_contains = '--anat_only') == 0
    # assert count_calls_to('fmriprep', call_list, call_contains = "--use-synth-DC") == 0
    # assert count_calls_to('ciftify_recon_all', call_list) == 0
    # assert count_calls_to('ciftify_subject_fmri', call_list) == 0

@patch('ciftify.bidsapp.run.run')
def test_default_one_subject_one_session_for_synth_noSDC(mock_run):

    uargs = [synth_bids, '/output/dir', 'participant', '--participant_label=02', '--session_label=01', '--no-SDC']
    ret = simple_main_run(uargs)
    call_list = parse_call_list_into_strings(mock_run.call_args_list)
    assert count_calls_to('fmriprep', call_list) > 0
    # assert count_calls_to('fmriprep', call_list, call_contains = "--use-synth-DC") == 0
    # assert count_calls_to('ciftify_recon_all', call_list) == 0
    # assert count_calls_to('ciftify_subject_fmri', call_list) == 0

@patch('ciftify.bidsapp.run.run')
def test_default_one_subject_one_session_for_ds7t_defaultSDC(mock_run):

    uargs = [ds7t_bids, '/output/dir', 'participant', '--participant_label=02', '--session_label=1']
    ret = simple_main_run(uargs)
    call_list = parse_call_list_into_strings(mock_run.call_args_list)
    assert count_calls_to('fmriprep', call_list) > 0
    # assert count_calls_to('fmriprep', call_list, call_contains = "--use-synth-DC") == 0
    # assert count_calls_to('ciftify_recon_all', call_list) == 0
    # assert count_calls_to('ciftify_subject_fmri', call_list) == 0

@patch('ciftify.bidsapp.run.run')
def test_default_one_subject_one_session_for_ds7t_ignorefieldmaps(mock_run):

    uargs = [ds7t_bids, '/output/dir', 'participant', '--participant_label=02', '--session_label=1', '--ignore-fieldmaps']
    ret = simple_main_run(uargs)
    call_list = parse_call_list_into_strings(mock_run.call_args_list)
    assert count_calls_to('fmriprep', call_list) > 0
    # assert count_calls_to('fmriprep', call_list, call_contains = "--synth-sdc") == 1
    # assert count_calls_to('fmriprep', call_list, call_contains = "--ignore-fieldmaps") == 1
    # assert count_calls_to('ciftify_recon_all', call_list) == 0
    # assert count_calls_to('ciftify_subject_fmri', call_list) == 0

@patch('ciftify.bidsapp.run.run')
def test_default_one_subject_one_session_for_synth_noSDC(mock_run):

    uargs = [ds7t_bids, '/output/dir', 'participant', '--participant_label=02', '--session_label=1', '--no-SDC']
    ret = simple_main_run(uargs)
    call_list = parse_call_list_into_strings(mock_run.call_args_list)
    assert count_calls_to('fmriprep', call_list) > 0
    # assert count_calls_to('fmriprep', call_list, call_contains = "--synth-sdc") == 0
    # assert count_calls_to('fmriprep', call_list, call_contains = "--ignore-fieldmaps") == 1
    # assert count_calls_to('ciftify_recon_all', call_list) == 0
    # assert count_calls_to('ciftify_subject_fmri', call_list) == 0


@patch('os.path.exists')
@patch('ciftify.bidsapp.run.run')
def test_one_participant_anat_ciftify_only_for_ds005(mock_run, mock_exists):

    ## create mock case where freesurfer output exists
    freesurfer_output_testfile = '/output/freesurfer/sub-14/mri/wmparc.mgz'
    mock_exists.side_effect = lambda path : True if path == freesurfer_output_testfile else False
    uargs = [ds7t_bids, '/output', 'participant', '--participant_label=02', '--anat_only']
    ret = simple_main_run(uargs)
    call_list = parse_call_list_into_strings(mock_run.call_args_list)
    assert count_calls_to('fmriprep', call_list,  call_contains = "--anat_only") == 0
    assert count_calls_to('ciftify_recon_all', call_list) == 1
    assert count_calls_to('ciftify_subject_fmri', call_list) == 0

@patch('os.path.exists')
@patch('ciftify.bidsapp.run.run')
def test_one_participant_fmri_ciftify_only_for_ds005(mock_run, mock_exists):

    ## create mock case where freesurfer output exists
    freesurfer_output_testfile = '/output/freesurfer/sub-14/mri/wmparc.mgz'
    mock_exists.side_effect = lambda path : True if path == freesurfer_output_testfile else False
    uargs = [ds005_bids, '/output/k', 'participant', '--participant_label=14', '--anat_only']
    ret = simple_main_run(uargs)
    call_list = parse_call_list_into_strings(mock_run.call_args_list)
    assert count_calls_to('fmriprep', call_list, call_contains = "--anat_only") == 0
    assert count_calls_to('ciftify_recon_all', call_list) == 1
    assert count_calls_to('ciftify_subject_fmri', call_list) > 0

print('test_default_all_participants_for_ds005()')
test_default_all_participants_for_ds005()
print('test_default_one_participant_for_ds005()')
test_default_one_participant_for_ds005()
print('test_default_two_participants_for_ds005()')
test_default_two_participants_for_ds005()
print('test_default_one_subject_one_session_for_synth_noSDC()')
test_default_one_subject_one_session_for_synth_noSDC()
print('test_one_participant_anat_ciftify_only_for_ds005()')
test_one_participant_anat_ciftify_only_for_ds005()
print('test_one_participant_fmri_ciftify_only_for_ds005()')
test_one_participant_fmri_ciftify_only_for_ds005()
    # also mock the fmriprep outputs
    # @patch('os.path.exists')
    # def test_one_participant_anat_ciftify_only_for_ds005(self, mock_run, mock_exists):
    #
    #     arguments = copy.deepcopy(self.docopt_args)
    #     arguments['<bids_dir>'] = ds005_bids
    #     arguments['--participant_label'] = '14'
    #     arguments['--anat-only'] = False
    #     ## create mock case where freesurfer output exists
    #     freesurfer_output_testfile = '/output/freesurfer/sub-14/mri/wmparc.mgz'
    #     mock_exists.side_effect = lambda path : True if path == freesurfer_output_testfile else False
    #     ret = simple_main_run(arguments)
    #     assert ret

## create situation where ciftify_recon_all is skipped

# bids/tests/data/ds005 - 16 subjects, 1 session, no fmap
# ds005_bids = os.path.join(get_test_data_path(), 'ds005')
# ds005_output = '/scratch/edickie/ds005_output'
# run(['mkdir -p', ds005_output])


# # bids/tests/data/7t_trt - 10 Subject, 2 sessions + fmap (phase) based on ds001168
# ds7t_bids = os.path.join(get_test_data_path(), '7t_trt')
# ds7t_out = '/tmp/ds7t_out'
#
# # bids/tests/data/synthetic - 5 subjects, 2 sessions, no fmap
# synth_bids = os.path.join(get_test_data_path(), 'synthetic')
# synth_out = '/tmp/synth_out'
# # it would be good to find/generate a test case with 1 session (i.e. no session struct) and fmaps..
# # note ds001393 "RewardBeast" on open neuro has this format..
# # note ds000256_R1.0.0 on open neuro also has this format..
# # individual brain Charting ds000244 is the only one I see with Repolar fieldmaps
#
# # writing my script of things that a functional test would do
#
# # user A (synthetic or ds005) runs all data with no fieldmaps from scratch
# # + default args
#
# run(['run.py', ds005_bids, ds005_output, 'participant', '--debug', '--dry-run',
#     '--participant_label=14'])
#
# run(['run.py', ds005_bids, ds005_output, 'participant', '--debug', '--dry-run',
#     '--participant_label=14', '--anat_only'])
# run(['run.py', synth_bids, synth_out, 'participant', '--debug', '--dry-run'])
# # + no sdc
# ## note run in synthetics and ds005 to insure that these flags work..
# # + filter for one session, filter for 2 sessions, not filtered for sessions
# run(['run.py', synth_bids, synth_out, 'participant', '--debug', '--dry-run', '--participant_label="02"'])
# run(['run.py', synth_bids, synth_out, 'participant', '--debug', '--dry-run', '--participant_label="03,04"'])
# # + filter for task
# run(['run.py', synth_bids, synth_out, 'participant', '--debug', '--dry-run', '--task_label=rest'])
# # + filter for one subject, two subjects, not filtering for subjects
# run(['run.py', synth_bids, synth_out, 'participant', '--debug', '--dry-run', '--session_label=01'])
#
# # user B (7t_trt) runs all data with fieldmaps from scratch
# # + default args (using fieldmaps)
# run(['run.py', ds7t_bids, ds7t_out, 'participant', '--debug', '--dry-run'])
#
# # + using ignore fieldmaps (should run syn-sdc)
# run(['run.py', ds7t_bids, ds7t_out, 'participant', '--debug', '--dry-run', '--ignore-fieldmaps'])
# # + no sdc
# run(['run.py', ds7t_bids, ds7t_out, 'participant', '--debug', '--dry-run', '--no-SDC'])

# user C runs (ds005) from freesurfer (note fieldmaps options shoudl not be effected by anat)

# user D runs (ds005) from freesurfer with --anat-only (should only run ciftify_recon_all steps)

# user E run (ds005) from fmriprep (runs ciftify_recon_all and ciftify_subject_fmri)

# - note this brings up the use case where the use may want to run
#   ciftify_subject_fmri in parallel (for many tasks/sessions) AFTER running ciftify_recon_all once
# user F run (ds005) from fmriprep skipping ciftify_recon_all...need to introduce flag for this..
