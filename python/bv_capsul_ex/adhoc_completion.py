
import os
import traits.api as traits
from capsul.process.attributed_process import AttributedProcess, \
    AttributedProcessFactory
from bv_capsul_ex.ex_processes import ThresholdProcess, Mask


class AttributedThresholdProcess(AttributedProcess):

    def __init__(self, process, study_config, name=None):
        super(AttributedThresholdProcess, self).__init__(process, study_config,
                                                         name)
        self.capsul_attributes.add_trait('input_directory', traits.Directory())
        self.capsul_attributes.add_trait('output_directory',
                                         traits.Directory())
        self.capsul_attributes.add_trait('array_filename', traits.Str())
        self.capsul_attributes.add_trait('extension', traits.Str())

    def complete_parameters(self, process_inputs={}):
        self.set_parameters(process_inputs)
        attrib = self.capsul_attributes
        self.process.array_file = os.path.join(
            attrib.input_directory, '%s.%s'
            % (attrib.array_filename, attrib.extension))
        self.process.mask_inf = os.path.join(
            attrib.output_directory, '%s_masked_inf.%s'
            % (attrib.array_filename, attrib.extension))
        self.process.mask_sup = os.path.join(
            attrib.output_directory, '%s_masked_sup.%s'
            % (attrib.array_filename, attrib.extension))

    @staticmethod
    def _factory(process, study_config, name):
        if isinstance(process, ThresholdProcess):
            return AttributedThresholdProcess(process, study_config, name)
        return None


class AttributedMask(AttributedProcess):

    def __init__(self, process, study_config, name=None):
        super(AttributedThresholdProcess, self).__init__(process, study_config,
                                                         name)
        self.capsul_attributes.add_trait('output_directory',
                                         traits.input_directory())
        self.capsul_attributes.add_trait('extension', traits.Str())

    def complete_parameters(self, process_inputs={}):
        self.set_parameters(process_inputs)
        attrib = self.capsul_attributes
        in_file = self.process.input
        if in_file not in (None, traits.Undefined, ''):
            if in_file.endswith('.%s' % atts.extension):
                in_file = in_file[:-len(atts.extension) - 1]
            else:
                dot = in_file.rfind('.')
                if dot >= 0:
                    in_file = in_file[:dot]
            self.process.output = os.path.join(
                attrib.output_directory, '%s_masked_inf.%s'
                % (in_file, attrib.extension))

    @staticmethod
    def _factory(process, study_config, name):
        if isinstance(process, Mask):
            return AttributedMask(process, study_config, name)
        return None


# register factories into AttributedProcessFactory
AttributedProcessFactory().register_factory(
    AttributedThresholdProcess._factory, 1000)
AttributedProcessFactory().register_factory(
    AttributedMask._factory, 1001)
