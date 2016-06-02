import os
from capsul.api import Process, Pipeline
from traits.api import File, List, Float, on_trait_change, Undefined
import numpy as np

def np_save(filename, array):
    np.save(filename, array)
    if not filename.endswith('.npy'):
        os.rename(filename + '.npy', filename)

class ThresholdProcess(Process):
    array_file = File()
    threshold = Float()
    mask_sup = File(output=True)
    mask_inf = File(output=True)

    def _run_process(self):
        print 'ThresholdProcess', self.array_file
        open(self.array_file).read()
        arr = np.load(open(self.array_file))
        mask_sup = (arr >= self.threshold)
        mask_inf = (arr < self.threshold)
        np_save(self.mask_sup, mask_sup)
        np_save(self.mask_inf, mask_inf)


class AverageProcess(Process):
    array_file = File()
    mask = File()
    average = File(output=True)

    def _run_process(self):
        print 'AverageProcess', self.array_file
        arr = np.load(self.array_file)
        mask = np.load(self.mask)
        arr[mask==False] = 0
        s = np.sum(arr)
        n = np.sum(mask)
        np_save(self.average, np.asarray([s / n, n]))


class ConvertInputs(Process):
    input_files = List(File)
    output_files = List(File, output=True)

    def _run_process(self):
        print 'ConvertInputs'
        for i in xrange(len(self.input_files)):
            r = open(self.input_files[i],'rb').read()
            open(self.output_files[i],'wb').write(r)

    @on_trait_change('input_files')
    def _input_files_changed(self):
        if self.output_files is Undefined or not self.output_files:
            self.output_files = [''] * len(self.input_files)
        elif len(self.output_files) < len(self.input_files):
            self.output_files += [''] * (len(self.input_files)
                                         - len(self.output_files))
        elif len(self.output_files) > len(self.input_files):
            self.output_files = self.output_files[:len(self.input_files)]

class Mask(Process):
    def __init__(self):
        super(Mask, self).__init__()
        self.add_trait('input', File())
        self.add_trait('mask', File())
        self.add_trait('output', File(output=True))

    def _run_process(self):
        print 'Mask'
        arr = np.load(self.input)
        mask = np.load(self.mask)
        arr[mask==False] = 0
        np_save(self.output, arr)

class AveragePipeline(Pipeline):
    def pipeline_definition(self):
        self.add_process('threshold', ThresholdProcess)
        self.add_process('average_sup', AverageProcess)
        self.add_process('average_inf', AverageProcess)
        self.add_process('template_mask_inf', Mask)
        self.add_process('template_mask_sup', Mask)
        self.export_parameter('threshold', 'array_file')
        #self.export_parameter('threshold', 'mask_sup', is_optional=True)
        #self.export_parameter('threshold', 'mask_inf', is_optional=True)
        self.add_link('array_file->average_sup.array_file')
        self.add_link('array_file->average_inf.array_file')
        self.add_trait('template_mask', File())
        self.add_link('template_mask->template_mask_sup.mask')
        self.add_link('template_mask->template_mask_inf.mask')
        self.add_link('template_mask_sup.output->average_sup.mask')
        self.add_link('template_mask_inf.output->average_inf.mask')
        self.add_link('threshold.mask_sup->template_mask_sup.input')
        self.add_link('threshold.mask_inf->template_mask_inf.input')
        self.export_parameter('average_sup', 'average', 'average_sup')
        self.export_parameter('average_inf', 'average', 'average_inf')
        self.node_position = {
            'threshold': (139.58311, 75.6937),
            'inputs': (0.0, 106.6937),
            'average_inf': (279.08311, 182.38873999999998),
            'average_sup': (279.08311, 0.0),
            'outputs': (407.47671, 75.6937)}



class GroupAverage(Process):
    def __init__(self):
        super(GroupAverage, self).__init__()
        self.add_trait('average_files', List(File()))
        self.add_trait('average', File(output=True))

    def _run_process(self):
        s = 0
        n = 0
        for fname in self.average_files:
            arr = np.load(fname)
            s += arr[0] * arr[1]
            n += arr[1]
        np_save(self.average, np.asarray([s / n, n]))


class GroupAveragePipeline(Pipeline):
    def pipeline_definition(self):
        self.add_process('check_inputs', ConvertInputs)
        self.add_iterative_process(
            'individual_avg', AveragePipeline(),
            ['array_file', 'average_sup', 'average_inf'],
            do_not_export=['mask_sup', 'mask_inf'])
        self.add_process('average_sup', GroupAverage())
        self.add_process('average_inf', GroupAverage())
        self.add_link('check_inputs.output_files->individual_avg.array_file')
        self.add_link('individual_avg.average_sup->average_sup.average_files')
        self.add_link('individual_avg.average_inf->average_inf.average_files')
        self.export_parameter('individual_avg', 'average_sup', 'averages_sup')
        self.export_parameter('individual_avg', 'average_inf', 'averages_inf')
        self.export_parameter('average_sup', 'average', 'group_average_sup')
        self.export_parameter('average_inf', 'average', 'group_average_inf')
        self.node_position = {
            'average_inf': (447.28569, 118.762),
            'average_sup': (447.28569, 4.306),
            'individual_avg': (289.06669, 125.0),
            'inputs': (0.0, 62.0),
            'outputs': (592.55429, 62.0),}

if __name__ == '__main__':
    import sys
    import os
    from tempfile import mkstemp
    from capsul.qt_gui.widgets.pipeline_developper_view \
        import PipelineDevelopperView
    from soma.qt_gui.qt_backend import QtGui
    
    qapp = None
    if QtGui.QApplication.instance() is None:
        qapp = QtGui.QApplication(sys.argv)
    pipeline = AveragePipeline()
    pipeline2 = GroupAveragePipeline()
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

