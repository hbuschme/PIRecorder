#! /usr/bin/python

# PIRecorder.py -- Record parasocial interactions with audiovisual media
# Copyright (C) 2013 Hendrik Buschmeier
#
# Initially based on Qt example for VLC Python bindings
# Copyright (C) 2009-2010 the VideoLAN team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.

from __future__ import division, print_function

import os.path
import sys
import time
import user

import vlc
from PyQt4 import QtGui, QtCore

class PIRecorder(QtGui.QMainWindow):
    """Parasocial Interaction Recorder."""

    def __init__(self, master=None, participant_id='dummy', response_path='.'):
        QtGui.QMainWindow.__init__(self, master)
        self.setWindowTitle("PIRecorder")

        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()

        self.createUI()
        self.pi_response_path = response_path
        self.pi_response_id = participant_id
        self.pi_response_file = None
        self.video_start_time = 0
        self.pi_response_counter = 0

    def createUI(self):
        self.widget = QtGui.QWidget(self)
        self.setCentralWidget(self.widget)

        if sys.platform == "darwin":
            self.videoframe = QtGui.QMacCocoaViewContainer(0)
        else:
            self.videoframe = QtGui.QFrame()
        self.palette = self.videoframe.palette()
        self.palette.setColor (QtGui.QPalette.Window,
                               QtGui.QColor(0,0,0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        self.hbuttonbox = QtGui.QHBoxLayout()
        self.playbutton = QtGui.QPushButton("Play")
        self.hbuttonbox.addWidget(self.playbutton)
        self.connect(self.playbutton, QtCore.SIGNAL("clicked()"),
                     self.Play)

        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addLayout(self.hbuttonbox)

        self.widget.setLayout(self.vboxlayout)

    def keyPressEvent(self, event):
        if self.video_start_time == 0:
            return
        if not event.isAutoRepeat(): 
            self.pi_response_counter += 1
            response_time = time.time() - self.video_start_time
            self.pi_response_file.write('{}, {}, {}\n'.format(self.pi_response_counter, response_time, event.key()))
            self.pi_response_file.flush()

    def Play(self):
        """play"""
        self.mediaplayer.play()
        self.video_start_time = time.time()
        self.playbutton.setVisible(False)

    def OpenFile(self, filename=None):
        if filename is None:
            filename = QtGui.QFileDialog.getOpenFileName(self, "Open File", user.home)
        if not filename:
            sys.exit(-1)

        self.media = self.instance.media_new(unicode(filename))
        self.mediaplayer.set_media(self.media)
        self.media.parse()

        if sys.platform == "linux2": # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32": # for Windows
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin": # for MacOS
            self.mediaplayer.set_nsobject(self.videoframe.winId())

        self.pi_response_file = open(self.pi_response_path + '/' + self.pi_response_id + '-' + os.path.splitext(os.path.basename(str(filename)))[0]+ '.csv', 'w')

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    player = PIRecorder()
    player.show()
    player.resize(800, 600)
    if sys.argv[1:]:    # videofile
        player.OpenFile(sys.argv[1])
        player.response_id = sys.argv[2]
        player.response_path = sys.argv[3]
    else:
        player.OpenFile(None)
    sys.exit(app.exec_())
