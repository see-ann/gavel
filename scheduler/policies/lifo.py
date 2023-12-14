import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import copy
import random

import job_id_pair
from policy import Policy, PolicyWithPacking


class LIFOPolicy(Policy):
    def __init__(self, mode='base', seed=None, packing_threshold=1.5):
        super().__init__()
        self._name = 'LIFO'
        self._mode = mode
        self._allocation = {}
        self._scale_factors = {}
        if mode == 'base':
            self._rng = random.Random()
            if seed is not None:
                self._rng.seed(seed)
        elif mode == 'packing':
            self._packing_threshold = packing_threshold

    def _pack(self, queue, throughputs, scale_factors):
        # Sample implementation of packing logic
        while len(queue) > 0:
            job_id_to_schedule = queue.pop(0)
            best_packed_job = None
            best_packed_throughput = 0

            for scheduled_job_id in self._allocation:
                if scheduled_job_id.is_pair() or scheduled_job_id == job_id_to_schedule:
                    continue

                potential_packed_job = job_id_pair.JobIdPair(scheduled_job_id, job_id_to_schedule)
                worker_type = self._allocation[scheduled_job_id]
                packed_throughput = throughputs[potential_packed_job][worker_type]

                if packed_throughput > best_packed_throughput:
                    best_packed_throughput = packed_throughput
                    best_packed_job = potential_packed_job

            if best_packed_throughput >= self._packing_threshold:
                self._allocation[best_packed_job] = self._allocation[scheduled_job_id]
                del self._allocation[scheduled_job_id]

    def get_allocation(self, throughputs, scale_factors, cluster_spec):
        available_workers = copy.deepcopy(cluster_spec)
        queue = [job_id for job_id in sorted(list(throughputs.keys()), reverse=True)
                if job_id not in self._allocation and not job_id.is_pair()]

        while queue:
            job_id_to_schedule = queue.pop(0)
            if self._mode == 'packing' and job_id_to_schedule in throughputs:
                self._pack(queue, throughputs, scale_factors)

            scale_factor = scale_factors[job_id_to_schedule]
            for worker_type, available_count in available_workers.items():
                if available_count >= scale_factor:
                    self._allocation[job_id_to_schedule] = worker_type
                    available_workers[worker_type] -= scale_factor
                    break

        # Construct final allocation
        final_allocation = {job_id: {worker_type: 0.0 for worker_type in cluster_spec}
                            for job_id in throughputs}
        for job_id, worker_type in self._allocation.items():
            if job_id in throughputs:  # Check if the job ID is in throughputs
                final_allocation[job_id][worker_type] = 1.0

        return final_allocation

