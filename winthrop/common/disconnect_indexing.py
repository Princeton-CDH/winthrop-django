'''pytest plugin to disconnect index signal handlers at the beginning
of the testing session'''


def pytest_sessionstart(session):
    from winthrop.common.signals import IndexableSignalHandler
    IndexableSignalHandler.disconnect()
