from nose.tools import assert_equals

from zuice.util import create_factory

def test_factory_for_a_class_passes_all_calls_to_build_to_that_classes_constructor():
    class Message(object):
        def __init__(self, text, severity):
            self.text = text
            self.severity = severity
            
    message_factory = create_factory(Message)
    message_text = "Comment added successfully"
    severity = "INFO"
    message = message_factory.build(message_text, severity=severity)
    assert_equals(message.text, message_text)
    assert_equals(severity, severity)
