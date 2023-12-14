# Develop & Evaluate Simple Scheduling Policies

This project focuses on developing and evaluating simple scheduling policies within a simulated cluster environment. We investigate the impact of various scheduling algorithms including FIFO, LIFO, SRTF, and Max-Min Fairness on cluster performance metrics.

## Getting Started

These instructions will guide you through setting up and running the project on your local machine for development and testing purposes.

### Prerequisites

- Docker installed on your system.

### Installation

1. **Build the Docker Image**:

   In the project's root directory (where the `Dockerfile` is located), run the following command to build the Docker image:

   ```bash
   docker build -t gavel .
   ```

   This builds a Docker image named `gavel` based on the specifications in `Dockerfile`.

2. **Run the Simulator**:

   Use the following command format to run the simulator with a specific scheduling policy:

   ```bash
   docker run gavel -t /scheduler/traces/physical_cluster/medium_test.trace --seed 42 -p [POLICY_NAME] -c 2:0:0
   ```

   Replace `[POLICY_NAME]` with the desired scheduling policy. Options include `fifo`, `lifo`, `srtf`, `max_min_fairness`, and others in the `policies` subdirectory.

   Example for LIFO policy:

   ```bash
   docker run gavel -t /scheduler/traces/physical_cluster/medium_test.trace --seed 42 -p lifo -c 2:0:0
   ```

### Customization

Customize the simulation by changing the scheduling policy or modifying the cluster specifications and workload traces.

## Acknowledgments

- This project is a fork of [Heterogeneity-Aware Cluster Scheduling Policies for Deep Learning Workloads](https://github.com/stanford-futuredata/gavel) by Stanford FutureData.
- Special thanks to Rui Pan for the inspiration from Idea #2 of the Research Project Discussions, and to all contributors and supporters of the original Gavel project.
