#!/usr/bin/env python

"""
Please find below a Python Sceleton, defining
- a Daemon class
- a main() function that instantiates that Daemon class
- the CLI constructor which runs the main class.

Your task:
Please fill this sceleton with code:

1) accept and read "config.json" file as config
2) scan the paths stated in that JSON file for new files
3) verify if that file is a text or binary file
3a) if binary: move it to /tmp/out/binary
3b) if text: move it to /tmp/out/text
4) If a file is delivered twice ( by filename ) - delete it
5) Create a MySQL Table and insert meta data (see config file for credentials)
5a) Insert: datetime, filename, input_filepath, output_filepath, type (binary/text)
6) Think about how to guarantee code quality

Extra:
- Keep in mind that this code should be run as a Daemon on an EC2 instance in the future.
- Think about how to inform other systems about new files arrived, ideally with AWS techniques

Use pip / virtualenv to install libraries.
Google is allowed, comments are welcome. 
Feel free to ask in case of questions.

"""

import cli.app


class Daemon(object):

    def __init__(self, params):
        self.params = params

    def wait(self):
        pass

@cli.app.CommandLineApp
def main(app):
    d = Daemon(app.params)
    def run():
        print(d.params)
    run()
    d.wait()


if __name__ == '__main__':
    main.add_param('-c', '--config')
    main.run()
