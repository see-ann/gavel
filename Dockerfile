# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container to /scheduler
WORKDIR /scheduler

# Install system dependencies required by scs, qdldl, and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Copy the scheduler directory and the entrypoint script into the container
COPY scheduler/ /scheduler
COPY entrypoint.sh /scheduler

# Make entrypoint.sh executable
RUN chmod +x /scheduler/entrypoint.sh

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /scheduler/requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Set the entrypoint script
ENTRYPOINT ["/scheduler/entrypoint.sh"]

# Set default arguments for the entrypoint script
CMD ["-t", "/scheduler/traces/physical_cluster/medium_test.trace", "--seed", "42", "-p", "fifo", "-c", "2:0:0"]
