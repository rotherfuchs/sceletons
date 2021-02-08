import sys, os, time, atexit, signal, logging
from logging.handlers import WatchedFileHandler


class Daemon:
    """A generic daemon class.

    Usage: subclass the daemon class and override the run() method.

    """

    def __init__(self, pidfile):
        self.pidfile = pidfile

        self.die = False # graceful dying
        self.logger = self._get_logger('/tmp/foo.log')

        self.logger.debug("\n")
        self.logger.debug("__init__() called.")

        signal.signal(signal.SIGINT, self._exit)
        signal.signal(signal.SIGTERM, self._exit)

        self.region = 'eu-central-1'


    def _get_logger(self, logpath=None):

        logger = logging.getLogger('ProfileTune Transcoder Daemon')
        logger.setLevel('DEBUG')

        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s]: %(module)s: %(process)d %(message)s', '%d %b %Y %H:%M:%S')

        if logpath is None:
            log_handler = logging.StreamHandler()

        else:
            log_handler = WatchedFileHandler(logpath)

        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)

        return logger


    def start(self):
        """Start the daemon."""

        self.logger.debug("start() called.")

        # Check for a pidfile to see if the daemon already runs
        try:
            with open(self.pidfile,'r') as pf:

                pid = int(pf.read().strip())

        except IOError:
            pid = None

        if pid:
            message = "pidfile {0} already exist. " + \
                    "Daemon already running?\n"
            self.logger.error(message.format(self.pidfile))

            sys.exit(1)

        # Start the daemon
        self.daemonize()

        try:
            self.run()
        except Exception as e:
            self.logger.error(e)


    def daemonize(self):
        """Deamonize class. UNIX double fork mechanism."""

        self.logger.debug("daemonize() called.")

        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)

        except OSError as err:
            self.logger.error('fork #1 failed: {0}\n'.format(err))
            sys.exit(1)

        # decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:

                # exit from second parent
                sys.exit(0)
        except OSError as err:
            self.logger.error('fork #2 failed: {0}\n'.format(err))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)

        pid = str(os.getpid())
        with open(self.pidfile,'w+') as f:
            f.write(pid + '\n')

        self.logger.info("Running as daemon. PID is %s" % pid)


    def delpid(self):
        """
        Destructor.

        I am called when I quit naturally (EOL).
        Otherwise, stop() is the destructor for unnatural exists
        (i.e. SIGNAL).

        """
        self.logger.debug("delpid() called.")

        os.remove(self.pidfile)

        self.logger.info("Program ended.")


    def stop(self):
        """
        Destructor.

        I am only called if I was killed unnaturally.

        """

        self.logger.debug("stop() called.")

        # Get the pid from the pidfile
        try:
            with open(self.pidfile,'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if not pid:
            message = "pidfile {0} does not exist. " + \
                    "Daemon not running?\n"
            sys.stderr.write(message.format(self.pidfile))
            return # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)

        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    self.delpid()
            else:
                self.logger.error(str(err.args))
                sys.exit(1)


    def _exit(self, signum, frame):
        self.logger.debug("_exit() called by %s" % signum)
        self.logger.info("Kill signal received. Stopping...")

        self.die = True


    def restart(self):
        """Restart the daemon."""
        self.logger.debug("restart() called.")
        self.stop()
        self.start()


    def run(self):
        """
        The actual business logic.

        It will be called after the process has been daemonized by
        start() or restart().

        """

        self.logger.debug("run() called.")

        while not self.die:
            self.logger.debug("Poll ...")

        self.logger.info("Stopped.")


if __name__ == '__main__':
    pidfile = "/tmp/d.pid"
    daemon = Daemon(pidfile)
    daemon.start()

    with open(pidfile, 'rb') as f:
        pid = f.read()

    self.stdout.write("Started with pid %s" % pid)

