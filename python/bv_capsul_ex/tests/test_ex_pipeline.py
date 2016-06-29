
from __future__ import print_function

import unittest
import os
import sys
import tempfile
import shutil
import subprocess
import numpy as npy
import glob
from capsul.api import StudyConfig, get_process_instance
from capsul.attributes.completion_engine import ProcessCompletionEngine
from capsul.attributes.attributes_schema import ProcessAttributes
from bv_capsul_ex import ex_processes

debug = False


class TestCapsulEx(unittest.TestCase):

    def setUp(self):
        tmpout = tempfile.mkdtemp(prefix='capsul_ex_test_')

        self.work_dir = tmpout
        print('working dir:', tmpout)
        self.input = os.path.join(self.work_dir, 'input_data')

        stdout = open(os.path.join(self.work_dir, 'stdout'), 'w')
        subprocess.check_call(['generate_data', self.input],
                              stdout=stdout, stderr=stdout)
        del stdout
        self.output = os.path.join(self.work_dir, 'output_data')

        study_config = StudyConfig(modules=['SomaWorkflowConfig',
                                            'AttributesConfig'])
        study_config.input_directory = self.input
        study_config.output_directory = os.path.join(
            self.work_dir, 'output_data')
        study_config.shared_directory = os.path.join(self.input, 'share')
        study_config.somaworkflow_computing_resource = 'localhost'
        study_config.somaworkflow_computing_resources_config.localhost = {
            'transfer_paths': [],
        }
        study_config.attributes_schema_paths += [
            'bv_capsul_ex.adhoc_completion',
            'bv_capsul_ex.tests.test_ex_pipeline',
            'bv_capsul_ex.schema']
        study_config.process_completion = 'bv_capsul_ex'
        study_config.attributes_schemas = {'input': 'bv_capsul_ex',
                                           'output': 'bv_capsul_ex',
                                           'shared': 'bv_capsul_shared'}
        self.study_config = study_config

    def tearDown(self):
        if os.path.exists(self.work_dir):
          if not debug:
              print('del test and dir:', self.work_dir)
              shutil.rmtree(self.work_dir)
          else:
              print('leaving existing directory:', self.work_dir)

    def setup_pipeline(self):
        input_dirs = glob.glob(os.path.join(
            self.input, 'database/random_matrix/lasagna/*'))
        self.groups = [os.path.basename(os.path.dirname(x))
                       for x in input_dirs]
        self.subjects = [os.path.basename(x) for x in input_dirs]
        self.input_files = [os.path.join(p, x + '.npy')
                            for p, x in zip(input_dirs, self.subjects)]
        self.pipeline = ex_processes.AveragePipeline()
        self.pipeline.set_study_config(self.study_config)
        self.pipeline2 = get_process_instance(
            'bv_capsul_ex.ex_processes.GroupAveragePipeline',
            self.study_config)
        self.pipeline.array_file = self.input_files[0]
        self.pipeline.template_mask = os.path.join(
            self.input, 'share/template_masks/amyelencephalic.npy')
        self.pipeline.threshold = 0.56
        self.pipeline.average_sup = os.path.join(
            self.output, 'oneshot_sup.npy')
        self.pipeline.average_inf = os.path.join(
            self.output, 'oneshot_inf.npy')

        self.pipeline2.input_files = [
            self.input_files[0],
            self.input_files[1],
        ]
        #self.pipeline2.template_mask = os.path.join(
            #self.input, 'share/template_masks/amyelencephalic.npy')
        #self.pipeline2.threshold = 0.56
        #self.pipeline2.group_average_sup = os.path.join(
            #self.output, 'group_sup.npy')
        #self.pipeline2.group_average_inf = os.path.join(
            #self.output, 'group_inf.npy')
        #self.pipeline2.averages_sup = [
            #os.path.join(self.output, '%s_sup.npy' % self.subjects[0]),
            #os.path.join(self.output, '%s_sup.npy' % self.subjects[1])
        #]
        #self.pipeline2.averages_inf = [
            #os.path.join(self.output, '%s_inf.npy' % self.subjects[0]),
            #os.path.join(self.output, '%s_inf.npy' % self.subjects[1])
        #]

    def test_structure(self):
        self.setup_pipeline()
        self.assertEqual(self.pipeline.nodes["average_sup"].process.array_file,
                         self.pipeline.array_file)
        self.study_config.use_soma_workflow = False
        self.pipeline()
        x_sup = npy.load(self.pipeline.average_sup)
        x_inf = npy.load(self.pipeline.average_inf)
        print('avg_sup:', x_sup)
        print('avg_inf:', x_inf)

    def pass_me(self):
        pass

    @unittest.skip('too long')
    def test_direct_run(self):
        self.setup_pipeline()
        self.study_config.use_soma_workflow = False
        self.pipeline2()

    @unittest.skip('too long')
    def test_full_wf(self):
        self.setup_pipeline()
        self.study_config.use_soma_workflow = True
        result = self.study_config.run(self.pipeline2)
        self.assertEqual(result, None)

    def test_process_adhoc_completion(self):
        study_config = self.study_config
        threshold = get_process_instance(
            'bv_capsul_ex.ex_processes.ThresholdProcess', study_config)
        athreshold = ProcessCompletionEngine.get_completion_engine(
            threshold, 'threshold')
        self.assertTrue(athreshold is not None)
        attrib = {
            'center': 'alpha_centauri',
            'subject': 'r2d2',
            'analysis': 'M0',
        }
        pinputs = {
            'capsul_attributes': attrib,
            'threshold': 0.43,
        }
        athreshold.complete_parameters(process_inputs=pinputs)
        self.assertEqual(athreshold.__class__.__name__,
                         'ThresholdProcessAdhocCompletion')
        self.assertEqual(threshold.array_file,
                         os.path.join(study_config.input_directory,
                                      'alpha_centauri_r2d2.npy'))
        self.assertEqual(threshold.threshold, 0.43)
        self.assertEqual(
            threshold.mask_inf,
            os.path.join(study_config.output_directory,
                         'alpha_centauri_r2d2_M0_thresholded_inf.npy'))
        self.assertEqual(
            threshold.mask_sup,
            os.path.join(study_config.output_directory,
                         'alpha_centauri_r2d2_M0_thresholded_sup.npy'))
        mask =  get_process_instance('bv_capsul_ex.ex_processes.Mask',
                                     study_config)
        amask = ProcessCompletionEngine.get_completion_engine(mask, 'mask')
        self.assertTrue(amask is not None)
        attrib = {
            'center': 'alpha_centauri',
            'subject': 'r2d2',
            'analysis': 'M0',
        }
        pinputs = {
            'capsul_attributes': attrib,
            'input': os.path.join(study_config.output_directory,
                                  'input_data_thresholded_inf.npy'),
        }
        amask.complete_parameters(process_inputs=pinputs)
        self.assertEqual(mask.input, pinputs['input'])
        self.assertEqual(mask.mask,
                         os.path.join(study_config.shared_directory,
                                      'template_masks/mask.npy'))
        self.assertEqual(mask.output,
                         os.path.join(study_config.output_directory,
                                      'input_data_thresholded_inf_masked.npy'))

    def test_pipeline_adhoc_completion(self):
        study_config = self.study_config
        pipeline = get_process_instance(
            'bv_capsul_ex.ex_processes.AveragePipeline', study_config)
        apipeline = ProcessCompletionEngine.get_completion_engine(
            pipeline, 'average_pipeline')
        self.assertTrue(apipeline is not None)
        attrib = {
            'center': 'alpha_centauri',
            'subject': 'r2d2',
            'analysis': 'M0',
            'mask_type': 'amyelencephalic',
        }
        pinputs = {
            'capsul_attributes': attrib,
            'threshold': 0.75,
        }
        self.assertEqual(
            sorted(apipeline.get_attribute_values().user_traits().keys()),
            ['analysis', 'center', 'mask_type', 'subject'])
        apipeline.complete_parameters(process_inputs=pinputs)
        self.assertEqual(pipeline.threshold, 0.75)
        self.assertEqual(
            pipeline.template_mask,
            os.path.join(study_config.shared_directory,
                         'template_masks/amyelencephalic.npy'))
        #self.assertEqual(
            #pipeline.nodes['threshold'].process.mask_inf,
            #os.path.join(study_config.output_directory,
                         #'input_data_thresholded_inf.npy'))
        #self.assertEqual(
            #pipeline.nodes['threshold'].process.mask_sup,
            #os.path.join(study_config.output_directory,
                         #'input_data_thresholded_sup.npy'))
        #self.assertEqual(
            #pipeline.nodes['template_mask_inf'].process.output,
            #os.path.join(study_config.output_directory,
                         #'input_data_thresholded_inf_masked.npy'))
        #self.assertEqual(
            #pipeline.nodes['template_mask_sup'].process.output,
            #os.path.join(study_config.output_directory,
                         #'input_data_thresholded_sup_masked.npy'))
        self.assertEqual(
            pipeline.nodes['average_inf'].process.average,
            os.path.join(
                study_config.output_directory,
                'alpha_centauri_r2d2_M0_average_inf.npy'))
        self.assertEqual(
            pipeline.nodes['average_sup'].process.average,
            os.path.join(
                study_config.output_directory,
                'alpha_centauri_r2d2_M0_average_sup.npy'))
        self.assertEqual(
            pipeline.average_inf,
            os.path.join(
                study_config.output_directory,
                'alpha_centauri_r2d2_M0_average_inf.npy'))
        self.assertEqual(
            pipeline.average_sup,
            os.path.join(
                study_config.output_directory,
                'alpha_centauri_r2d2_M0_average_sup.npy'))

    @unittest.skip("broken test for now")
    def test_group_pipeline_adhoc_completion(self):
        self.setup_pipeline()
        study_config = self.study_config
        agpipeline = ProcessCompletionEngine.get_completion_engine(
            self.pipeline2, 'group_average_pipeline')
        self.assertTrue(agpipeline is not None)
        attrib = {
            'center': self.groups,
            'subject': self.subjects,
            'mask_type': 'amyelencephalic',
            'analysis': ['M0'],
        }
        pinputs = {
            'capsul_attributes': attrib,
            'threshold': 0.55,
            'input_files': self.input_files
        }
        self.assertEqual(
            sorted(agpipeline.get_attribute_values().user_traits().keys()),
            ['analysis', 'center', 'mask_type', 'subject'])
        agpipeline.complete_parameters(process_inputs=pinputs)
        for ifname in self.pipeline2.input_files:
            self.assertTrue(os.path.exists(ifname))
        self.assertEqual(len(self.pipeline2.averages_sup), len(self.subjects))

        # run sequentially
        study_config.use_soma_workflow = False
        res = study_config.run(self.pipeline2)
        self.assertEqual(res, None)
        for ofname in self.pipeline2.averages_sup:
            self.assertTrue(os.path.exists(ofname))
        for ofname in self.pipeline2.averages_inf:
            self.assertTrue(os.path.exists(ofname))
        self.assertTrue(os.path.exists(self.pipeline2.group_average_sup))
        self.assertTrue(os.path.exists(self.pipeline2.group_average_inf))


def test():
    """ Function to execute unitest
    """
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCapsulEx)
    runtime = unittest.TextTestRunner(verbosity=2).run(suite)
    return runtime.wasSuccessful()


if __name__ == "__main__":
    verbose = False
    if len(sys.argv) >= 2 and ('-v' in sys.argv[1:]
                               or '--verbose' in sys.argv[1:]):
        verbose = True
    if len(sys.argv) >= 2 and ('-d' in sys.argv[1:]
                               or '--debug' in sys.argv[1:]):
        debug = True

    print("RETURNCODE: ", test())

    if verbose:
        test = TestCapsulEx('pass_me')
        test.setUp()
        test.setup_pipeline()
        #from tempfile import mkstemp
        from capsul.qt_gui.widgets.pipeline_developper_view \
            import PipelineDevelopperView
        from soma.qt_gui.qt_backend import QtGui

        qapp = None
        if QtGui.QApplication.instance() is None:
            qapp = QtGui.QApplication(sys.argv)
        pipeline = test.pipeline
        pipeline2 = test.pipeline2
        pv = PipelineDevelopperView(pipeline, show_sub_pipelines=True,
                                    allow_open_controller=True)
        pv.auto_dot_node_positions()
        pv2 = PipelineDevelopperView(pipeline2, show_sub_pipelines=True,
                                    allow_open_controller=True)
        pv2.auto_dot_node_positions()
        pv.show()
        pv2.show()

        ## .npy extension is mandatory otherwise it is added
        ## by numpy.save.
        #tmp =  [mkstemp(suffix='.npy') for i in xrange(10)]
        #mask = np.zeros((5, 5))

        #try:
            #pipeline2.output_files = [i[1] for i in tmp]
            #pipeline2.run()
        #finally:
            #for t in tmp:
                #os.close(t[0])
                #os.remove(t[1])
        if qapp is not None:
            qapp.exec_()

        test.tearDown()
        del test


