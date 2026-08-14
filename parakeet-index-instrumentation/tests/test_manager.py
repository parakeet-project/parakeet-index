import parakeet_index_instrumentation as instrumentation
from parakeet_index_instrumentation.base import root_manager


def test_root_manager_add_dispatcher():
    dispatcher = instrumentation.get_dispatcher("test")

    assert "root" in root_manager.dispatchers
    assert "test" in root_manager.dispatchers
