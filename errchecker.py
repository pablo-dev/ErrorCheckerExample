import os
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class CustomFileSystemEventHandle(FileSystemEventHandler):

    def __init__(self):
        self.fileErrorChk = open("/tmp/errchecker-log.txt", 'ab', 0)
        self.errorCounter = 0

        self.filesDict = {}
        for filename in os.listdir(path):
            try:
                filepath = os.path.join(path, filename)
                if os.path.isfile(filepath):
                    file = open(filepath, 'r')
                    file.read()
                    self.filesDict[filepath] = file
            except UnicodeDecodeError:
                print('Not able to read ' + file.name)

    def print_changes(self, file):
        try:
            for line in file:
                if "Exception:" in line or "ERROR" in line:
                    self.fileErrorChk.write(bytes(line, 'UTF-8'))
                    self.errorCounter += 1
                elif "INFO: Server startup in:" in line:
                    self.fileErrorChk.write(bytes("TOMCAT IS STARTED with " + str(self.errorCounter) + " errors\n", 'UTF-8'))
                    self.errorCounter = 0
        except UnicodeDecodeError:
            print('Not able to read ' + file.name)

    def on_created(self, event):
        if os.path.isfile(event.src_path):
            self.filesDict[event.src_path] = open(event.src_path, 'r')
            self.print_changes(self.filesDict[event.src_path])

    def on_modified(self, event):
        if os.path.isfile(event.src_path):
            self.print_changes(self.filesDict[event.src_path])

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fileErrorChk.close()
        for filename, file in self.filesDict.items():
            file.close

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'

    event_handler = CustomFileSystemEventHandle()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()