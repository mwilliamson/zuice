from nose.tools import assert_equals

from zuice.util import factory

def test_factory_for_a_class_passes_all_calls_to_build_to_that_classes_constructor():
    class Message(object):
        def __init__(self, text, severity):
            self.text = text
            self.severity = severity
            
    message_factory = factory(Message)()
    message_text = "Comment added successfully"
    severity = "INFO"
    message = message_factory.build(message_text, severity=severity)
    assert_equals(message.text, message_text)
    assert_equals(severity, severity)

def test_factory_class_for_a_class_has_name_of_class_followed_by_factory():
    class Message(object):
        pass
            
    assert_equals(factory(Message).__name__, "MessageFactory")
