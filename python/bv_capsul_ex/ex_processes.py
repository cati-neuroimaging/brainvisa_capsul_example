
from capsul.api import Process, Pipeline
from traits import api as traits
import numpy as np


class ThresholdProcess(Process):
    def __init__(self):
        super(ThresholdProcess, self).__init__()
        self.add_trait('array_file', traits.File())
        self.add_trait('threshold', traits.Float())
        self.add_trait('mask_sup', traits.File(output=True))
        self.add_trait('mask_inf', traits.File(output=True))

    def _run_process(self):
        print 'ThresholdProcess.'
        arr = np.load(self.array_file)
        mask_sup = (arr >= self.threshold)
        mask_inf = (arr < self.threshold)
        np.save(self.mask_sup, mask_sup)
        np.save(self.mask_inf, mask_inf)


class AverageProcess(Process):
    def __init__(self):
        super(AverageProcess, self).__init__()
        self.add_trait('array_file', traits.File())
        self.add_trait('mask', traits.File())
        self.add_trait('average', traits.File(output=True))

    def _run_process(self):
        print 'AverageProcess.'
        arr = np.load(self.array_file)
        mask = np.load(self.mask)
        arr[mask==False] = 0
        s = np.sum(arr)
        n = np.sum(mask)
        np.save(self.average, np.asarray([s / n, n]))


class AveragePipeline(Pipeline):
    def pipeline_definition(self):
        self.add_process('threshold', ThresholdProcess())
        self.add_process('average_sup', AverageProcess())
        self.add_process('average_inf', AverageProcess())
        self.export_parameter('threshold', 'array_file')
        self.export_parameter('threshold', 'mask_sup', is_optional=True)
        self.export_parameter('threshold', 'mask_inf', is_optional=True)
        self.add_link('array_file->average_sup.array_file')
        self.add_link('array_file->average_inf.array_file')
        self.add_link('threshold.mask_sup->average_sup.mask')
        self.add_link('threshold.mask_inf->average_inf.mask')
        self.export_parameter('average_sup', 'average', 'average_sup')
        self.export_parameter('average_inf', 'average', 'average_inf')
        self.node_position = {
            'threshold': (139.58311, 75.6937),
            'inputs': (0.0, 106.6937),
            'average_inf': (279.08311, 182.38873999999998),
            'average_sup': (279.08311, 0.0),
            'outputs': (407.47671, 75.6937)}


class UnzipSubjects(Process):
    def __init__(self):
        super(UnzipSubjects, self).__init__()
        self.add_trait('zip_file', traits.File())
        self.add_trait('output_files',
                       traits.List(traits.File(output=True), output=True))

    def _run_process(self):
        for fname in self.output_files:
            arr = np.random.random((5, 5))
            np.save(fname, arr)

class GroupAverage(Process):
    def __init__(self):
        super(GroupAverage, self).__init__()
        self.add_trait('average_files', traits.List(traits.File()))
        self.add_trait('average', traits.File(output=True))

    def _run_process(self):
        s = 0
        n = 0
        for fname in self.average_files:
            arr = np.load(fname)
            s += arr[0] * arr[1]
            n += arr[1]
        np.save(self.average, np.asarray([s / n, n]))


class GroupAveragePipeline(Pipeline):
    def pipeline_definition(self):
        self.add_process('unzip', UnzipSubjects())
        self.add_iterative_process(
            'individual_avg', AveragePipeline(),
            ['array_file', 'average_sup', 'average_inf'],
            do_not_export=['mask_sup', 'mask_inf'])
        self.add_process('average_sup', GroupAverage())
        self.add_process('average_inf', GroupAverage())
        self.export_parameter('unzip', 'zip_file')
        self.export_parameter('average_sup', 'average', 'average_sup')
        self.export_parameter('average_inf', 'average', 'average_inf')
        self.add_link('unzip.output_files->individual_avg.array_file')
        self.add_link('individual_avg.average_sup->average_sup.average_files')
        self.add_link('individual_avg.average_inf->average_inf.average_files')
        self.node_position = {
            'average_inf': (447.28569, 118.762),
            'average_sup': (447.28569, 4.306),
            'individual_avg': (289.06669, 125.0),
            'inputs': (0.0, 62.0),
            'outputs': (592.55429, 62.0),
            'unzip': (136.66689, 23.843)}


if __name__ == '__main__':
    import sys
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
    if qapp is not None:
        qapp.exec_()

