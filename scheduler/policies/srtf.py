
import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import copy
import random

import job_id_pair
from policy import Policy, PolicyWithPacking

class SRTFPolicy(Policy):
    def __init__(self, seed=None):
        super().__init__()
        self._name = 'SRTF'
        self._allocation = {}
        self._scale_factors = {}
        self._remaining_times = {}  # Tracks remaining execution time for jobs
        self._rng = random.Random(seed) if seed is not None else random.Random()

    def update_remaining_times(self, job_updates):
        # This method should be called to update the remaining times of jobs
        for job_id, remaining_time in job_updates.items():
            self._remaining_times[job_id] = remaining_time

    def get_allocation(self, throughputs, scale_factors, cluster_spec):
        available_workers = copy.deepcopy(cluster_spec)

        # Sort jobs by remaining time. The shortest remaining time job is first
        sorted_jobs = sorted(self._remaining_times, key=self._remaining_times.get)

        for job_id in sorted_jobs:
            if job_id in self._allocation:
                continue  # Skip already allocated jobs

            scale_factor = scale_factors[job_id]
            for worker_type in available_workers:
                if available_workers[worker_type] >= scale_factor:
                    # Allocate this worker to the job
                    self._allocation[job_id] = worker_type
                    available_workers[worker_type] -= scale_factor
                    break  # Break as the job is allocated

        # Construct the final allocation
        final_allocation = {}
        for job_id in throughputs:
            final_allocation[job_id] = {worker_type: 0.0 for worker_type in cluster_spec}
        for job_id, worker_type in self._allocation.items():
            final_allocation[job_id][worker_type] = 1.0

        return final_allocation
