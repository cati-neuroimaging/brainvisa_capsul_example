from __future__ import print_function

from capsul.attributes_schema import AttributesSchema, EditableAttributes, ProcessAttributes
from traits.api import String


class BrainvisaTestSchema(AttributesSchema):
    schema_name = 'bv_capsul_ex'
    
    class Acquisition(EditableAttributes):
        center = String()
        subject = String()
    
    class Group(EditableAttributes):
        group = String()

    class Processing(EditableAttributes):
        analysis = String()

class BrainvisaTestSharedSchema(AttributesSchema):
    schema_name = 'bv_capsul_shared'

class AveragePipelineAttributes(ProcessAttributes):
    def __init__(self, process, schema):
        super(AveragePipelineAttributes, self).__init__(process, schema)
        
        self.set_parameter_attributes('array_file', 'input', 'Acquisition', dict(type='array'))
        self.set_parameter_attributes('average_sup', 'output', ['Acquisition', 'Processing'], dict(type='average', threshold='sup'))
        self.set_parameter_attributes('average_inf', 'output', ['Acquisition', 'Processing'], dict(type='average', threshold='inf'))
        
        self.set_parameter_attributes('template', 'shared', ['Acquisition', 'Processing'], dict(type='average', threshold='inf'))


if __name__ == '__main__':
    import six
    from capsul.api import get_process_instance
    from capsul.attributes_schema import AttributesSchemaFactory
    from pprint import pprint
    
    process = get_process_instance('bv_capsul_ex.ex_processes.AveragePipeline')
    
    asm = AttributesSchemaFactory()
    asm.module_path.append('bv_capsul_ex.schema')
    
    schema = asm.get_attributes_schema('bv_capsul_ex')
    schema_shared = asm.get_attributes_schema('bv_capsul_ex')
    
    process_attributes = AveragePipelineAttributes(process, dict(input=schema, output=schema, shared=schema_shared))
    process_attributes.center = 'the_center'
    process_attributes.subject = 'the_subject'
    process_attributes.analysis = 'the_analysis'
    for name, trait in six.iteritems(process_attributes.user_traits()):
        print(name, trait)
    pprint(process_attributes.get_parameters_attributes())

    pprint(process_attributes.parameter_attributes)