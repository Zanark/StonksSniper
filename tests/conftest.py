from __future__ import annotations

import pytest


@pytest.fixture(scope="session")
def qt_application():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def qt_events(qt_application):
    from PySide6.QtCore import QCoreApplication, QEvent

    yield
    # processEvents alone does not deliver deleteLater without an outer event loop.
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    qt_application.processEvents()
