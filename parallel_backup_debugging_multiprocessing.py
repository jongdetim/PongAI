"""
Runs evaluation functions in parallel subprocesses
in order to evaluate multiple genomes at once.
"""
from multiprocessing import Pool
# import signal


class ParallelEvaluator(object):
    def __init__(self, num_workers, eval_function, timeout=None):
        """
        eval_function should take one argument, a tuple of
        (genome object, config object), and return
        a single float (the genome's fitness).
        """
        self.num_workers = num_workers
        self.eval_function = eval_function
        self.timeout = timeout
        self.pool = Pool(num_workers)
        
        # Register a signal handler for KeyboardInterrupt
        # signal.signal(signal.SIGINT, self._handle_interrupt)

    def _handle_interrupt(self, *args):
        # # Terminate the worker processes when KeyboardInterrupt is received
        print("HEY I GOT TO _HANDLE_INTERRUPT :))")
        # # self.pool.close() # should this be terminate?
        # # self.pool.join()
        self.pool.terminate()

    def __del__(self, *args):
        print("killing all child processes")
        self.pool.close() # should this be terminate?
        # self.pool.terminate()
        self.pool.join()

    def evaluate(self, genomes, config):
        jobs = []
        for ignored_genome_id, genome in genomes:
            # jobs.append(self.pool.apply_async(self.eval_function, (genome, config)))
            try:
                # job = self.pool.apply_async(self.eval_function, (genome, config, exit_flag), error_callback=self._handle_interrupt)
                job = self.pool.apply_async(self.eval_function, (genome, config), error_callback=self._handle_interrupt)
                # print("appending job")
                jobs.append(job)
            except:
                print("error in apply_async")
                self._handle_interrupt(None, None)
                raise Exception("error in apply_async")

        # assign the fitness back to each genome
        for job, (ignored_genome_id, genome) in zip(jobs, genomes):
            genome.fitness = job.get(timeout=self.timeout)
            # print("finished job")
