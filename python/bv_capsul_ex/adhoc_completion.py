
import os
import traits.api as traits
from capsul.attributes.attributes_schema import ProcessAttributes
from capsul.attributes.completion_engine import ProcessCompletionEngine, \
  ProcessCompletionEngineFactory
from bv_capsul_ex.ex_processes import ThresholdProcess, Mask, AverageProcess, \
    AveragePipeline, GroupAveragePipeline


class ThresholdProcessAdhocCompletion(ProcessCompletionEngine):
    def complete_parameters(self, process_inputs={}):
        self.set_parameters(process_inputs)
        study_config = self.process.get_study_config()
        attrib = self.get_attribute_values().get_parameters_attributes()
        print(attrib)
        self.process.array_file = os.path.join(
            study_config.input_directory, '%s_%s.npy'
            % (attrib['array_file']['center'],
               attrib['array_file']['subject']))
        self.process.mask_inf = os.path.join(
            study_config.output_directory, '%s_%s_%s_thresholded_%s.npy'
            % (attrib['mask_inf']['center'],
               attrib['mask_inf']['subject'],
               attrib['mask_inf']['analysis'],
               attrib['mask_inf']['threshold']))
        self.process.mask_sup = os.path.join(
            study_config.output_directory, '%s_%s_%s_thresholded_%s.npy'
            % (attrib['mask_sup']['center'],
               attrib['mask_sup']['subject'],
               attrib['mask_sup']['analysis'],
               attrib['mask_sup']['threshold']))


class ThresholdProcessAdhocCompletionFactory(ProcessCompletionEngineFactory):
    factory_id = 'bv_capsul_ex'

    def get_completion_engine(self, process, name):
        if isinstance(process, ThresholdProcess):
            return ThresholdProcessAdhocCompletion(process, name)
        return ProcessCompletionEngine(process, name)


#class AttributedMask(AttributedProcess):

    #def __init__(self, process, study_config, name=None):
        #super(AttributedMask, self).__init__(process, study_config,
                                                         #name)
        #self.capsul_attributes.add_trait('extension', traits.Str())

    #def complete_parameters(self, process_inputs={}):
        #self.set_parameters(process_inputs)
        #attrib = self.capsul_attributes
        #in_file = self.process.input
        #if in_file not in (None, traits.Undefined, ''):
            #if in_file.endswith('.%s' % attrib.extension):
                #in_file = in_file[:-len(attrib.extension) - 1]
            #else:
                #dot = in_file.rfind('.')
                #if dot >= 0:
                    #in_file = in_file[:dot]
            #self.process.output = os.path.join(
                #self.study_config.output_directory, '%s_masked.%s'
                #% (in_file, attrib.extension))

    #@staticmethod
    #def _factory(process, study_config, name):
        #if isinstance(process, Mask):
            #return AttributedMask(process, study_config, name)
        #return None


#class AttributedAverageProcess(AttributedProcess):

    #def __init__(self, process, study_config, name=None):
        #super(AttributedAverageProcess, self).__init__(process, study_config,
                                                       #name)
        #self.capsul_attributes.add_trait('extension', traits.Str())

    #def complete_parameters(self, process_inputs={}):
        #self.set_parameters(process_inputs)
        #attrib = self.capsul_attributes
        #in_file = self.process.array_file
        #if in_file not in (None, traits.Undefined, ''):
            #in_file = os.path.basename(in_file)
            #if in_file.endswith('.%s' % attrib.extension):
                #in_file = in_file[:-len(attrib.extension) - 1]
            #else:
                #dot = in_file.rfind('.')
                #if dot >= 0:
                    #in_file = in_file[:dot]
            #in_mask = self.process.mask
            #if in_mask not in (None, traits.Undefined, ''):
                #in_mask = os.path.basename(in_mask)
                #if in_mask.endswith('.%s' % attrib.extension):
                    #in_mask = in_mask[:-len(attrib.extension) - 1]
                #else:
                    #dot = in_mask.rfind('.')
                    #if dot >= 0:
                        #in_mask = in_mask[:dot]
                #self.process.average = os.path.join(
                    #self.study_config.output_directory, '%s_%s_average.%s'
                    #% (in_file, in_mask, attrib.extension))

    #@staticmethod
    #def _factory(process, study_config, name):
        #if isinstance(process, AverageProcess):
            #return AttributedAverageProcess(process, study_config, name)
        #return None


#class AttributedAveragePipeline(AttributedProcess):

    #def __init__(self, process, study_config, name=None):
        #super(AttributedAveragePipeline, self).__init__(process, study_config,
                                                        #name)
        #self.merge_controllers(self.capsul_attributes,
                               #self.get_nodes_attributes_controller())

    #@staticmethod
    #def _factory(process, study_config, name):
        #if isinstance(process, AveragePipeline):
            #return AttributedAveragePipeline(process, study_config, name)
        #return None


#class AttributedGroupAveragePipeline(AttributedProcess):

    #def __init__(self, process, study_config, name=None):
        #super(AttributedGroupAveragePipeline, self).__init__(
              #process, study_config, name)
        #self.capsul_attributes.add_trait('group', traits.List(traits.Str()))
        #self.capsul_attributes.add_trait('subject', traits.List(traits.Str()))
        #self.capsul_attributes.add_trait('extension', traits.Str())
        #self.capsul_attributes.add_trait('template', traits.Str())

    #def complete_parameters(self, process_inputs={}):
        #self.set_parameters(process_inputs)
        #attrib = self.capsul_attributes
        #sconfig = self.study_config
        #self.process.input_files = [
            #os.path.join(
                #sconfig.input_directory, 'database/random_matrix',
                #group, subject,
                #'%s.%s' % (subject, attrib.extension))
            #for group, subject in zip(attrib.group, attrib.subject)
        #]
        #self.process.template_mask = os.path.join(
            #sconfig.input_directory, 'share/template_masks',
            #'%s.%s' % (attrib.template, attrib.extension))
        #self.process.averages_sup = [
            #os.path.join(
                #sconfig.output_directory, 'database/group_average',
                #group, subject,
                #'%s_avg_sup.%s' % (subject, attrib.extension))
            #for group, subject in zip(attrib.group, attrib.subject)
        #]
        #self.process.averages_inf = [
            #os.path.join(
                #sconfig.output_directory, 'database/group_average',
                #group, subject,
                #'%s_avg_inf.%s' % (subject, attrib.extension))
            #for group, subject in zip(attrib.group, attrib.subject)
        #]
        #self.process.group_average_sup = \
            #os.path.join(sconfig.output_directory, 'database/group_average',
                         #'%s_sup.%s' % (attrib.template, attrib.extension))
        #self.process.group_average_inf = \
            #os.path.join(sconfig.output_directory, 'database/group_average',
                         #'%s_inf.%s' % (attrib.template, attrib.extension))

    #@staticmethod
    #def _factory(process, study_config, name):
        #if isinstance(process, GroupAveragePipeline):
            #return AttributedGroupAveragePipeline(process, study_config, name)
        #return None


