#===============================================================================
# Utilities for logging
#===============================================================================
import logging, os, sys, traceback

map_log_levels = { 'INFO': logging.INFO,
  'WARNING': logging.WARNING,
  'ERROR': logging.ERROR,
  'DEBUG': logging.DEBUG
}

def setup_app_logger(log_name, log_level, log_file, show_stdout=False):
    """
    Get a logger instance where you can easily log records
    
    It setups the main configuration for the logger, by default
    with a file handler.
    
    Then, in each module you can use it as:
        logger = logging.getLogger(__name__)
        logger.info("YAY")
    """
    try:
        log_level = map_log_levels.get(log_level, logging.INFO)
        logger = logging.getLogger(log_name)
        logger.setLevel(log_level)
        
        formatter = logging.Formatter("%(asctime)s  %(levelname)-8s %(name)-17s %(message)s") # [%(threadName)-8s] 
        
        # File handler
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.mkdir(log_dir)

        hdlr = logging.FileHandler(log_file)
        hdlr.setFormatter(formatter)
        hdlr.setLevel(log_level)
        logger.addHandler(hdlr)
        
        # For dev purposes
        if show_stdout:
            hdlr_stdout = logging.StreamHandler(sys.__stdout__)
            hdlr_stdout.setFormatter(formatter)
            hdlr_stdout.setLevel(log_level)
            logger.addHandler(hdlr_stdout)
        
        return logger
    except Exception:
        print_exception("Error message while setting the logger '%s'" % log_name)
        sys.exit(-1)   

#############################################
# OTHERS
#############################################
def print_exception(msg=""):
    error = sys.exc_info()[1]
    sys.stderr.write("%s: %s\n" % (msg, error))
    traceback.print_exc()
