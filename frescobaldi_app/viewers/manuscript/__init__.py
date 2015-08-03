# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2011 - 2014 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
A tool to display an engraver's copy in a dock.
"""

from __future__ import unicode_literals

import os

from PyQt4.QtCore import QSettings, Qt
from PyQt4.QtGui import (
    QAction, QKeySequence, QVBoxLayout, QToolButton,
    QHBoxLayout, QPushButton, QMessageBox)

import actioncollection
import actioncollectionmanager
import app
import icons
import panel
import userguide.util

import viewers
from viewers import popplerwidget
from viewers import documents

class ManuscriptViewPanel(viewers.AbstractViewPanel):
    """Manuscript Viewer Tool."""
    def __init__(self, mainwindow):
        super(ManuscriptViewPanel, self).__init__(mainwindow)
        self.toggleViewAction().setShortcut(QKeySequence("Meta+Alt+A"))
        mainwindow.addDockWidget(Qt.RightDockWidgetArea, self)

    def translateUI(self):
        self.setWindowTitle(_("Manuscript"))
        self.toggleViewAction().setText(_("Manuscript Viewer"))

    def _createConcreteActions(self, panel):
        return ManuscriptViewerActions(self)

    def _createConcreteWidget(self):
        """Create the widget for the panel"""
        from . import widget
        return widget.ManuscriptViewWidget(self)

    def _openViewdocsCaption(self):
        """Returns the caption for the file open dialog."""
        return app.caption(_("dialog title", "Open Manuscript(s)"))

    @viewers.activate
    def reloadView(self):
        active_manuscript = self.widget().currentDocument()
        if active_manuscript:
            reread = documents.Document(active_manuscript.filename())
            mds = self.actionCollection.viewer_document_select
            mds.replaceManuscript(active_manuscript, reread)


class ManuscriptViewerActions(viewers.ViewerActions):
    name = "manuscript"

    def _createViewdocChooserAction(self, panel):
        """Create the concrete ViewdocChooserAction."""
        return ManuscriptViewdocChooserAction(panel)

    def translateUI(self):
        super(ManuscriptViewerActions, self).translateUI()
        self.viewer_document_select.setText(_("Select Manuscript Document"))
        self.viewer_open.setText(_("Open manuscript(s)"))
        self.viewer_open.setIconText(_("Open"))
        self.viewer_close.setText(_("Close manuscript"))
        self.viewer_close.setIconText(_("Close"))
        self.viewer_close_other.setText(_("Close other manuscripts"))
        self.viewer_close_all.setText(_("Close all manuscripts"))

    def title(self):
        return _("Manuscript")


class ManuscriptViewdocChooserAction(viewers.ViewdocChooserAction):
    """Extends the parent class and also keeps track of when a document is
    opened or closed in the manuscript viewer.
    """

    def __init__(self, panel):
        super(ManuscriptViewdocChooserAction, self).__init__(panel)

    def slotEditdocChanged(self, doc):
        """Called when the mainwindow changes its current document."""
        # for now do nothing
        # when we have a tie between documents and manuscripts
        # something will have to be done here
        pass

    def slotEditdocUpdated(self, doc, job):
        """Called when a Job, finished on the document, has created new PDFs."""
        # for now do nothing
        pass

    def documentFiles(self):
        """Return a list with the filenames of all documents."""
        # TODO: Consider if it makes sense to cache that.
        # May be useless because *then* you'd have to add a slot to
        # update whenever _documents is changed.
        result = []
        for d in self._viewdocs:
            result.append(d.filename())
        return result

    def addManuscript(self, document):
        """Add a manuscript to our chooser."""
        self._viewdocs.append(document)
        self._currentIndex = len(self._viewdocs) - 1
        self.updateDocument()

    def replaceManuscript(self, olddoc, newdoc):
        """Instead of adding a new document replace an existing."""
        try:
            docindex = self._viewdocs.index(olddoc)
            self._viewdocs[docindex] = newdoc
            self.updateDocument()
        except ValueError:
            # no replacement possible because the original doc isn't found
            pass

    def setActiveDocument(self, filename, update = True):
        """Activate the given document if it's in the list of documents"""
        filenames = [d.filename() for d in self._viewdocs]
        if filename in filenames:
            self._currentIndex = filenames.index(filename)
            if update:
                self.updateDocument()
