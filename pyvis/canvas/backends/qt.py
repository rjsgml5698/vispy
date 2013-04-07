from pyvis.event import Event
from pyvis.canvas import CanvasBackend

import pyvis
qt_lib = pyvis.config['qt_lib']
if qt_lib == 'any':
    try: 
        from PyQt4 import QtGui, QtCore, QtOpenGL
    except ImportError:
        from PySide import QtGui, QtCore, QtOpenGL
elif qt_lib == 'pyqt':
    from PyQt4 import QtGui, QtCore
elif qt_lib == 'pyside':
    from PySide import QtGui, QtCore
else:
    raise Exception("Do not recognize Qt library '%s'. Options are 'pyqt', 'pyside', or 'any'." % str(qt_lib))
    

class QtCanvasBackend(QtOpenGL.QGLWidget, CanvasBackend):
    """Qt backend for Canvas abstract class."""
    
    ## Note: In this case, the backend is split into two classes since the 
    ## name 'geometry' would otherwise conflict with QWidget.geometry.
    
    def __init__(self, parent=None):
        ## before creating widget, make sure we have a QApplication
        if QtGui.QApplication.instance() is None:
            global QAPP
            QAPP = QtGui.QApplication([])
        CanvasBackend.__init__(self)
        QtOpenGL.QGLWidget.__init__(self, parent)

        
    @property
    def _pyvis_geometry(self):
        g = self.geometry()
        return (g.x(), g.y(), g.width(), g.height())
    
    def _pyvis_resize(self, w, h):
        self.resize(w, h)
        
    def _pyvis_show(self):
        self.show()
        
    def _pyvis_update(self):
        self.update()
        
    def _pyvis_run(self):
        return QtGui.QApplication.exec_()

    def initializeGL(self):
        if self._pyvis_canvas is None:
            return
        self._pyvis_canvas.events.initialize()
        
    def resizeGL(self, w, h):
        if self._pyvis_canvas is None:
            return
        ev = Event(size=(w,h))
        self._pyvis_canvas.events.resize(ev)

    def paintGL(self):
        if self._pyvis_canvas is None:
            return
        ev = Event(region=(0, 0, self.width(), self.height()))
        self._pyvis_canvas.events.paint(ev)
        
    def mousePressEvent(self, ev):
        if self._pyvis_canvas is None:
            return
        ev2 = QtMouseEvent(
            name='press', 
            qt_event=ev,
            pos=(ev.pos().x(), ev.pos().y()),
            button=int(ev.button()),
            )
        self._pyvis_canvas.events.mouse(ev2)
            
    def mouseReleaseEvent(self, ev):
        if self._pyvis_canvas is None:
            return
        ev2 = QtMouseEvent(
            name='release', 
            qt_event=ev,
            pos=(ev.pos().x(), ev.pos().y()),
            button=int(ev.button()),
            )
        self._pyvis_canvas.events.mouse(ev2)

    def mouseMoveEvent(self, ev):
        if self._pyvis_canvas is None:
            return
        ev2 = QtMouseEvent(
            name='move', 
            qt_event=ev,
            pos=(ev.pos().x(), ev.pos().y()),
            )
        self._pyvis_canvas.events.mouse(ev2)
        
    def wheelEvent(self, ev):
        if self._pyvis_canvas is None:
            return
        ev2 = Event( 
            name='wheel', 
            qt_event=ev,
            delta=ev.delta(),
            pos=(ev.pos().x(), ev.pos().y()),
            )
        self._pyvis_canvas.events.mouse(ev2)

class QtMouseEvent(Event):
    ## special subclass of Event for propagating acceptance info back to Qt.
    def accept(self):
        Event.accept(self)
        self.qt_event.accept()
