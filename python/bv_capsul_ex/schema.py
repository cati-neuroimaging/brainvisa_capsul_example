from __future__ import print_function

from capsul.attributes.attributes_schema import AttributesSchema, \
    EditableAttributes, ProcessAttributes
from traits.api import String


class BrainvisaTestSchema(AttributesSchema):
    factory_id = 'bv_capsul_ex'
    
    class Acquisition(EditableAttributes):
        center = String()
        subject = String()
    
    class Group(EditableAttributes):
        group = String()

    class Processing(EditableAttributes):
        analysis = String()

class BrainvisaTestSharedSchema(AttributesSchema):
    factory_id = 'bv_capsul_shared'

    class Mask(EditableAttributes):
        mask_type = String()


class AveragePipelineAttributes(ProcessAttributes):
    factory_id = 'AveragePipeline'

    def __init__(self, process, schema_dict):
        super(AveragePipelineAttributes, self).__init__(process, schema_dict)

        self.set_parameter_attributes('array_file', 'input', 'Acquisition',
                                      dict(type='array'))
        self.set_parameter_attributes('average_sup', 'output',
                                      ['Acquisition', 'Processing'],
                                      dict(type='average', threshold='sup'))
        self.set_parameter_attributes('average_inf', 'output',
                                      ['Acquisition', 'Processing'],
                                      dict(type='average', threshold='inf'))
        self.set_parameter_attributes('template_mask', 'shared', 'Mask',
                                      dict(type='array'))


class ThresholdAttributes(ProcessAttributes):
    factory_id = 'ThresholdProcess'

    def __init__(self, process, schema_dict):
        super(ThresholdAttributes, self).__init__(process, schema_dict)

        self.set_parameter_attributes('array_file', 'input', 'Acquisition',
                                      dict(type='array'))
        self.set_parameter_attributes('mask_sup', 'output',
                                      ['Acquisition', 'Processing'],
                                      dict(type='array', threshold='sup'))
        self.set_parameter_attributes('mask_inf', 'output',
                                      ['Acquisition', 'Processing'],
                                      dict(type='array', threshold='inf'))


class MaskAttributes(ProcessAttributes):
    factory_id = 'Mask'

    def __init__(self, process, schema_dict):
        super(MaskAttributes, self).__init__(process, schema_dict)

        self.set_parameter_attributes('input', 'input', 'Acquisition',
                                      dict(type='array'))
        self.set_parameter_attributes('mask', 'shared', 'Mask',
                                      dict(type='array', mask_type='mask'))
        self.set_parameter_attributes('output', 'output',
                                      ['Acquisition', 'Processing'],
                                      dict(type='array'))



if __name__ == '__main__':
    import six
    from capsul.api import get_process_instance
    from capsul.attributes_factory import AttributesFactory
    from pprint import pprint
    
    process = get_process_instance('bv_capsul_ex.ex_processes.AveragePipeline')
    
    factory = AttributesFactory()
    factory.module_path.append('bv_capsul_ex.schema')
    
    schema = factory.get('schema', 'bv_capsul_ex')
    schema_shared = factory.get('schema', 'bv_capsul_ex')
    
    process_attributes = AveragePipelineAttributes(process, dict(input=schema, output=schema, shared=schema_shared))
    process_attributes.center = 'the_center'
    process_attributes.subject = 'the_subject'
    process_attributes.analysis = 'the_analysis'
    for name, trait in six.iteritems(process_attributes.user_traits()):
        print(name, trait)
    pprint(process_attributes.get_parameters_attributes())

    pprint(process_attributes.parameter_attributes)