# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013-2018 by Igor E. Novikov
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import wal
from sk1 import config, events, appconst
from sk1.document import DocArea
from sk1.parts.ctxpanel import AppCtxPanel
from sk1.parts.doctabs import DocTabs
from sk1.parts.palettepanel import AppHPalette, AppVPalette
from sk1.parts.plgarea import PlgArea
from sk1.parts.statusbar import AppStatusbar
from sk1.parts.tools import AppTools
from sk1.pwidgets import RulerSurface, HRulerSurface, VRulerSurface
from sk1.pwidgets import CanvasSurface
from uc2 import uc2const


class MDIArea(wal.VPanel):
    app = None
    mw = None
    docareas = []
    ctxpanel = None
    current_docarea = None

    def __init__(self, app, parent):
        self.app = app
        self.mw = parent
        self.docareas = []
        wal.VPanel.__init__(self, parent)

        self.ctxpanel = AppCtxPanel(self.app, self)
        self.doc_tabs = DocTabs(app, self,
                                config.ui_style != appconst.GUI_CLASSIC)

        if config.ui_style == appconst.GUI_CLASSIC:
            if not wal.IS_MAC:
                self.pack(wal.HLine(self), fill=True)
            self.pack(self.ctxpanel, fill=True, padding=1)
            self.pack(self.doc_tabs, fill=True)

        if config.ui_style == appconst.GUI_TABBED:
            self.pack(self.doc_tabs, fill=True)
            self.pack(self.ctxpanel, fill=True, padding=2)
            self.pack(wal.PLine(self), fill=True)

        # ===== Main part
        hpanel = wal.HPanel(self)
        self.pack(hpanel, expand=True, fill=True)

        # ----- Tools
        self.tools = AppTools(self.app, hpanel)
        hpanel.pack(self.tools, fill=True, padding_all=2)
        hpanel.pack(wal.PLine(hpanel), fill=True)

        self.splitter = wal.Splitter(hpanel)

        # ----- Doc Area
        self.grid_panel = wal.GridPanel(self.splitter)
        self.grid_panel.add_growable_col(1)
        self.grid_panel.add_growable_row(1)
        self.corner = RulerSurface(self.app, self.grid_panel)
        self.grid_panel.add(self.corner)
        self.hruler = HRulerSurface(self.app, self.grid_panel)
        self.grid_panel.pack(self.hruler, fill=True)
        self.vruler = VRulerSurface(self.app, self.grid_panel)
        self.grid_panel.pack(self.vruler, fill=True)

        int_grid = wal.GridPanel(self.grid_panel)
        int_grid.add_growable_col(0)
        int_grid.add_growable_row(0)
        self.canvas = CanvasSurface(self.app, int_grid)
        int_grid.pack(self.canvas, fill=True)
        self.vscroll = wal.ScrollBar(int_grid)
        int_grid.pack(self.vscroll, fill=True)
        self.hscroll = wal.ScrollBar(int_grid, vertical=False)
        int_grid.pack(self.hscroll, fill=True)
        self.viewer = wal.VPanel(int_grid)
        int_grid.pack(self.viewer, fill=True)

        self.canvas._set_scrolls(self.hscroll, self.vscroll)
        self.grid_panel.pack(int_grid, fill=True)

        # ----- Doc Area End
        self.plg_area = PlgArea(self.app, self.splitter)
        self.app.mdiarea = self
        self.app.plg_area = self.plg_area

        self.splitter.split_vertically(self.grid_panel, self.plg_area)
        self.splitter.set_min_size(200)
        self.splitter.set_sash_gravity(1.0)
        self.splitter.unsplit()
        hpanel.pack(self.splitter, expand=True, fill=True)

        # ----- Vertical Palette panel
        self.vp_panel = wal.HPanel(hpanel)
        self.vp_panel.pack(wal.PLine(self.vp_panel), fill=True)
        vpalette_panel = AppVPalette(self.vp_panel, self.app)
        self.vp_panel.pack(vpalette_panel, fill=True, padding=2)
        hpanel.pack(self.vp_panel, fill=True, start_padding=2)
        if config.palette_orientation == uc2const.HORIZONTAL:
            self.vp_panel.hide()

        # ----- Horizontal Palette panel
        self.hp_panel = wal.VPanel(self)
        self.hp_panel.pack(wal.PLine(self.hp_panel), fill=True)
        hpalette_panel = AppHPalette(self.hp_panel, self.app)
        self.hp_panel.pack(hpalette_panel, fill=True, padding=2)
        self.pack(self.hp_panel, fill=True)

        self.change_palette()

        # ----- Status bar
        self.pack(wal.PLine(self), fill=True)
        self.statusbar = AppStatusbar(self)
        self.pack(self.statusbar, fill=True, padding=2)

        self.layout()
        events.connect(events.CONFIG_MODIFIED, self.config_update)

    def config_update(self, *args):
        if args[0] == 'palette_orientation':
            self.change_palette()

    def change_palette(self):
        if config.palette_orientation == uc2const.VERTICAL:
            self.hp_panel.hide()
            self.vp_panel.show()
        else:
            self.hp_panel.show()
            self.vp_panel.hide()

    def create_docarea(self, doc):
        docarea = DocArea(doc)
        docarea.doc_tab = self.doc_tabs.add_new_tab(doc)
        self.docareas.append(docarea)
        self.corner.refresh(clear=False)
        self.hruler.refresh(clear=False)
        self.vruler.refresh(clear=False)
        self.canvas.refresh(clear=False)
        self.canvas.update_scrolls()
        return docarea

    def remove_doc(self, doc):
        docarea = doc.docarea
        self.docareas.remove(docarea)
        self.doc_tabs.remove_tab(doc)
        if not self.docareas:
            self.mw.show_mdi(False)
            self.current_docarea = None
        else:
            if docarea == self.current_docarea:
                self.set_active(self.docareas[-1].presenter)

    def set_tab_title(self, docarea, title):
        docarea.doc_tab.set_title(title)

    def set_active(self, doc):
        doc_area = doc.docarea
        self.current_docarea = doc_area
        self.doc_tabs.set_active(doc)
        if len(self.docareas) == 1:
            self.mw.show_mdi(True)
        self.corner.refresh(clear=False)
        self.hruler.refresh(clear=False)
        self.vruler.refresh(clear=False)
        self.canvas.refresh(clear=False)
        self.canvas.update_scrolls()

    def show_plugin_area(self, value=True):
        if value:
            if not self.plg_area.is_shown():
                self.splitter.split_vertically(self.grid_panel,
                                               self.plg_area,
                                               config.sash_position)
        else:
            if self.plg_area.is_shown():
                w = self.splitter.get_size()[0]
                config.sash_position = self.splitter.get_sash_position() - w
                self.splitter.unsplit()
