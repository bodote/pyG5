import time

def repeat_until_true(self, func, max_attempts=None, delay=0):
    """
    Repeatedly calls the given function until it returns True.

    Args:
    func (callable): The function to be called repeatedly.
    max_attempts (int, optional): Maximum number of attempts. If None, will try indefinitely.
    delay (float, optional): Delay in seconds between attempts.

    Returns:
    bool: True if func() eventually returned True, False if max_attempts was reached.

    Raises:
    Any exception raised by func() will be propagated.
    """
   
    self.logger.debug("repeat loop start")
    attempts = 0
    while max_attempts is None or attempts < max_attempts:
        if func(self):
            return True
        self.logger.debug("repeat loop false")
        attempts += 1
        if delay > 0:
            time.sleep(delay)
    raise Exception("repeat loop false") 
