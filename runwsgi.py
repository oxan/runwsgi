#!/usr/bin/env python3
# Copyright (C) 2020 Oxan van Leeuwen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import os.path
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from wsgiref.simple_server import make_server
from importlib import import_module, reload

# parse arguments
parser = argparse.ArgumentParser(description='Simple WSGI server with hot reload support.')
parser.add_argument('application', help='application script or module name')
parser.add_argument('-p', '--port', default=8000, type=int, help='port to listen on')
args = parser.parse_args()

# find the directory in which the application resides, and add it to the import path
application_path_absolute = os.path.abspath(args.application)
application_dir = os.path.dirname(application_path_absolute)
application_module_name, _ = os.path.splitext(os.path.basename(application_path_absolute))

# import the application
sys.path.insert(0, application_dir)
import_module(application_module_name)
application = getattr(sys.modules[application_module_name], 'application')

# figure out all files that are imported from the application directory
reload_watches = {}
for module in sys.modules.values():
	if getattr(module, '__file__', None) is None:
		continue
	if not module.__file__.startswith(application_dir + '/'):
		continue
	reload_watches[module.__file__] = module

# handler to reload files when they are changed
class ReloadHandler(FileSystemEventHandler):
	def on_modified(self, event):
		print(f"# Reloading {reload_watches[event.src_path].__name__} from {event.src_path} due to modification...")
		reload(reload_watches[event.src_path])

		# reset the application, in case it was reloaded
		application = getattr(sys.modules[application_module_name], 'application')
		wsgi_server.set_app(application)

# wire-up the reloading to the filesystem watcher
handler = ReloadHandler()
observer = Observer()
for path in reload_watches.keys():
	print(f"# Watching {path} for modifications...")
	observer.schedule(handler, path)
observer.start()

# and finally start the WSGI server
wsgi_server = make_server('', args.port, application)
print(f"# Listening on port {args.port} for HTTP requests...")

wsgi_server.serve_forever()
