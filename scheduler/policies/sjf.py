import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import copy
import random

import job_id_pair
from policy import Policy, PolicyWithPacking

class SJFPolicy(Policy):
    def __init__(self, job_lengths=10, seed=None):
        self._name = 'SJF'
        self._allocation = {}
        self._scale_factors = {}
        self._job_lengths = job_lengths
        self._rng = random.Random()
        if seed is not None:
            self._rng.seed(seed)

    def get_allocation(self, throughputs, scale_factors, cluster_spec):
        available_workers = copy.deepcopy(cluster_spec)
        queue = []

        # Update the internal representation of scale_factors.
        for job_id in scale_factors:
            self._scale_factors[job_id] = scale_factors[job_id]

        # Add all jobs that have not been allocated already to the queue.
        # In SJF, jobs should be added in order of their expected completion
        # time or length.
        for job_id in sorted(list(throughputs.keys()), key=lambda j: self._job_lengths[j]):
            if job_id not in self._allocation and not job_id.is_pair():
                queue.append(job_id)

        # Rest of the implementation is similar to the FIFO policy.
        # Find all completed jobs, schedule jobs off the queue to replace
        # them, and determine how many workers are available.
        for scheduled_job_id in sorted(list(self._allocation.keys())):
            worker_type = self._allocation[scheduled_job_id]
            # Check if job has completed.
            if scheduled_job_id not in throughputs:
                for single_job_id in scheduled_job_id.singletons():
                    if single_job_id in throughputs:
                        queue.append(single_job_id)
                        queue.sort(key=lambda j: self._job_lengths[j])
                if len(queue) > 0:
                    job_id_to_schedule = queue[0]
                    if (scale_factors[job_id_to_schedule] <=
                            available_workers[worker_type]):
                        worker_type = self._allocation[scheduled_job_id]
                        if throughputs[job_id_to_schedule][worker_type] > 0.0:
                            queue.pop(0)
                            self._allocation[job_id_to_schedule] = worker_type
                            available_workers[worker_type] -= \
                                scale_factors[job_id_to_schedule]
                del self._allocation[scheduled_job_id]
                del self._scale_factors[scheduled_job_id]
            else:
                # Job has not completed, subtract its allocated workers
                # from available_workers.
                available_workers[worker_type] -= \
                    scale_factors[scheduled_job_id]

        # Allocate resources to as many jobs as possible.
        while len(queue) > 0:
            job_id_to_schedule = queue.pop(0)
            scale_factor = scale_factors[job_id_to_schedule]
            for worker_type in sorted(available_workers):
                if available_workers[worker_type] >= scale_factor:
                    if throughputs[job_id_to_schedule][worker_type] > 0.0:
                        self._allocation[job_id_to_schedule] = worker_type
                        available_workers[worker_type] -= scale_factor
                        break

        # Construct output allocation.
        final_allocation = {}
        for job_id in throughputs:
            final_allocation[job_id] = \
                    {worker_type: 0.0 for worker_type in cluster_spec}
        for job_id, worker_type in self._allocation.items():
            final_allocation[job_id][worker_type] = 1.0

        return final_allocation

# Example usage
# job_lengths = {job_id: length, ...}
# sjf_policy = SJFPolicy(job_lengths, seed=42)
