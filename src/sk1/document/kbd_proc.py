# -*- coding: utf-8 -*-
#
#	Copyright (C) 2015 by Igor E. Novikov
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import wx

from sk1.resources import pdids

class Kbd_Processor:

	canvas = None

	def __init__(self, canvas):
		self.canvas = canvas
		self.app = canvas.app
		self.actions = self.app.actions

	def on_key_down(self, event):
		key_code = event.GetKeyCode()
		raw_code = event.GetRawKeyCode()
		modifiers = event.GetModifiers()

		if key_code == wx.WXK_NUMPAD_DECIMAL and modifiers == wx.ACCEL_SHIFT:
			self.actions[wx.ID_CUT].do_call()
			return

		if key_code == wx.WXK_NUMPAD0 and modifiers == wx.ACCEL_SHIFT:
			self.actions[wx.ID_PASTE].do_call()
			return

		msg = "key:%d,raw:%d,modifers:%d" % \
		(key_code, raw_code, modifiers)
#		print msg
		event.Skip()

	def on_char(self, event):
#		print "OnChar Called"
		modifiers = event.GetModifiers()
		key_code = event.GetUniChar()
		char = unichr(event.GetUniChar())
		msg = "key:%d, modifers:%d, char:%s" % \
		(key_code, modifiers, char)
#		print msg
		event.Skip()
