import heapq
import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import copy
import random

import job_id_pair
from policy import Policy, PolicyWithPacking

class SJFPolicy(Policy):
    def __init__(self, seed=None):
        self._name = 'SJF'
        self._allocation = {}
        self._rng = random.Random()
        self._scale_factors = {}
        if seed is not None:
            self._rng.seed(seed)

    def estimate_job_duration(self, job_id, scale_factors):
        """Heuristic to estimate job duration based on scale factor."""
        # Simple heuristic: inverse of scale factor
        return 1.0 / scale_factors.get(job_id, 1)

    def get_allocation(self, throughputs, scale_factors, cluster_spec):
        available_workers = copy.deepcopy(cluster_spec)
        queue = []

        # Update the internal representation of scale_factors.
        for job_id in scale_factors:
            self._scale_factors[job_id] = scale_factors[job_id]

        # Reset the allocation.
        self._allocation = {}

        # Add all jobs that have not been allocated already to the queue.
        # Jobs are sorted by estimated duration (shortest first).
        for job_id in sorted(list(throughputs.keys())):
            if job_id not in self._allocation and not job_id.is_pair():
                estimated_duration = self.estimate_job_duration(job_id, scale_factors)
                heapq.heappush(queue, (estimated_duration, job_id))

        # Allocate resources to jobs based on SJF order
        while len(queue) > 0 and any(available_workers.values()):
            _, job_id_to_schedule = heapq.heappop(queue)
            worker_type = self.select_worker_type(job_id_to_schedule, available_workers, throughputs)
            if worker_type:
                self._allocation[job_id_to_schedule] = worker_type
                available_workers[worker_type] -= scale_factors[job_id_to_schedule]

        # Construct output allocation.
        final_allocation = {job_id: {worker_type: 0.0 for worker_type in cluster_spec} for job_id in throughputs}
        for job_id, worker_type in self._allocation.items():
            final_allocation[job_id][worker_type] = 1.0

        return final_allocation

    def select_worker_type(self, job_id, available_workers, throughputs):
        """Selects the best worker type for a job based on availability and throughput."""
        best_worker_type = None
        best_throughput = 0.0
        for worker_type in available_workers:
            if available_workers[worker_type] >= self._scale_factors[job_id]:
                throughput = throughputs[job_id][worker_type]
                if throughput > best_throughput:
                    best_throughput = throughput
                    best_worker_type = worker_type
        return best_worker_type
