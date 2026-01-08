""" Commandline Server """ # pylint: disable=invalid-name,abstract-method
import argparse
import datetime
import logging
import os
import time

import uvicorn

import OpenStackFlavorExporter.main

# create simple Logger to updateCache messages to console
LOG = logging.getLogger('updateCache')
HANDLER = logging.StreamHandler()
HANDLER.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s", datefmt='%Y-%d-%m %I:%M:%S %z')
HANDLER.setFormatter(formatter)
LOG.addHandler(HANDLER)
LOG.setLevel(logging.DEBUG)

def update_cache():
    """
    Helper function. Updates cached data continuously.
    """
    LOG.info("Start updating cached data continuously.")
    while True:
        start = datetime.datetime.now()
        OpenStackFlavorExporter.main.update_cache()
        stop = datetime.datetime.now()
        runningtime = (stop-start).seconds
        LOG.info("Updating cached data took %d seconds.", runningtime)
        sleepingtime = max(0, int(OpenStackFlavorExporter.main.MEMCACHEEXPIREAFTER/2)-runningtime)
        LOG.info("Sleeping for %d seconds.", sleepingtime)
        time.sleep(sleepingtime)

if __name__ == '__main__':

    PARSER = argparse.ArgumentParser("Run a OpenStackFlavorExpoertServer.")
    PARSER.add_argument("--memcachedHost",
                        help="Combination of host:port where a memcached server listened.",
                        type=str,
                        default="127.0.0.1:11211")
    PARSER.add_argument("--memcachedPrefix",
                        help="Prefix for memcached keys",
                        type=str,
                        default='')
    PARSER.add_argument("--bind",
                        help="Bind address for REST API server.",
                        type=str,
                        default="127.0.0.1:8080")
    PARSER.add_argument("--workers",
                        help="Number of available Workers ",
                        type=int,
                        default=4)
    PARSER.add_argument("--timeout",
                        help="Seconds until uvicorn worker timeouts.",
                        type=int,
                        default=300)

    ARGS = PARSER.parse_args()

    # validate arguments
    MEMCACHEDHOST = ARGS.memcachedHost
    MEMCACHEDPREFIX= ARGS.memcachedPrefix
    BIND = ARGS.bind.split(":")
    WORKERS = ARGS.workers
    TIMEOUT = ARGS.timeout

    # configure memcached
    OpenStackFlavorExporter.main.configure_memcache(enabled=True,
                                                  host=MEMCACHEDHOST,
                                                  expire=TIMEOUT,
                                                  prefix=MEMCACHEDPREFIX)

    # run uvicorn in a separate child process
    if os.fork() == 0:
        # child
        config = uvicorn.Config(
            app=OpenStackFlavorExporter.main.app,
            host=BIND[0],
            port=int(BIND[1]),
            log_level="info",
            workers=WORKERS,
            timeout_keep_alive=TIMEOUT)
        server = uvicorn.Server(config)
        server.run()
    else:
        # parent
        update_cache()
