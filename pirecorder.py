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

import argparse
import os.path
import sys
import time
import user

import vlc
from PyQt4 import QtGui, QtCore

class PIRecorder(QtGui.QMainWindow):
    '''Parasocial Interaction Recorder.'''

    def __init__(self, participant_id, output_path, verbose=False, master=None):
        QtGui.QMainWindow.__init__(self, master)
        self.setWindowTitle("PIRecorder")

        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()

        self.create_ui()

        self._output_path = output_path
        self._participant_id = participant_id
        self._verbose = verbose
        
        self._output_file = None
        
        self._t_video_started = 0
        self._is_playing = False
        self._is_paused = False
        self._response_counter = 0
        self._total_pause_dur = 0

    def create_ui(self):
        self.widget = QtGui.QWidget(self)
        self.setCentralWidget(self.widget)

        if sys.platform == 'darwin':
            self.videoframe = QtGui.QMacCocoaViewContainer(0)
        else:
            self.videoframe = QtGui.QFrame()

        self.palette = self.videoframe.palette()
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0,0,0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        self.label_start = QtGui.QPushButton('Press any key to start')
        self.label_cont = QtGui.QPushButton('Press any key to continue')
        #self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label_start.setStyleSheet("font: 18pt;");
        self.label_cont.setStyleSheet("font: 18pt;");

        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.videoframe)
        self.layout.addWidget(self.label_start)
        self.widget.setLayout(self.layout)

    def keyPressEvent(self, event):
        if not self._is_playing:
            self.play()
        elif self._is_paused:
            self.resume()
        elif event.key() == 80:
            self.pause()
        else:
            if not event.isAutoRepeat(): 
                self._response_counter += 1
                t_keypress = time.time() - self._t_video_started - self._total_pause_dur
                output = '{}, {}, {}\n'.format(self._response_counter, t_keypress, event.key())
                self._output_file.write(output)
                self._output_file.flush()
                if self._verbose:
                    print(output)

    def play(self):
        """play"""
        self.mediaplayer.play()
        self._t_video_started = time.time()
        self._is_playing = True
        self.label_start.setVisible(False)

    def pause(self):
        """pause"""
        self.mediaplayer.pause()
        self._t_video_paused = time.time()
        self._is_paused = True
        self.label_cont.setVisible(True)
        self.layout.addWidget(self.label_cont)
        self.widget.setLayout(self.layout)

    def resume(self):
        """resume after pause"""
        self.mediaplayer.play()
        self._total_pause_dur += time.time() - self._t_video_paused
        self._t_video_paused = None
        self._is_paused = False
        self.label_cont.setVisible(False)

    def open_file(self, filename=None):
        if filename is None:
            filename = QtGui.QFileDialog.getOpenFileName(self, "Open File", user.home)
        if not filename:
            sys.exit()

        self.media = self.instance.media_new(unicode(filename))
        self.mediaplayer.set_media(self.media)
        self.media.parse()

        if sys.platform == "linux2": # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32": # for Windows
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin": # for MacOS
            self.mediaplayer.set_nsobject(self.videoframe.winId())

        self._output_file = open(self._output_path + '/' + self._participant_id + '-' + os.path.splitext(os.path.basename(str(filename)))[0]+ '.csv', 'w')

    def clean_up(self):
        self._output_file.close()

def main():
    parser = argparse.ArgumentParser(description='Keystroke based parasocial interaction recorder.')
    parser.add_argument('-m', '--maximised', dest='maximised', action='store_true')#, default=True, type=bool)
    parser.add_argument('-f', '--media-file', dest='filename', default=None)
    parser.add_argument('-pid', '--participant-id', dest='participant_id', default='dummy')
    parser.add_argument('-o', '--out-path', dest='out_path', default='.')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true')
    args = parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    pir = PIRecorder(
        participant_id=args.participant_id,
        output_path=args.out_path,
        verbose=args.verbose)
    pir.show()

    if args.maximised:
        pir.showMaximized()
    else:
        pir.resize(800,600)
    pir.open_file(args.filename)
    ret = app.exec_()
    pir.clean_up()
    sys.exit(ret)

if __name__ == '__main__':
    main()
