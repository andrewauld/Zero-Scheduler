# Zero-Scheduler
Energy-aware scheduler implemented in a local KinD environment.

This project attempts to provide a pathway to achieving reduced power consumption in Kubernetes clusters. It does this
by implementing a regression model into the default Kubernetes scheduler as an extender plugin, which is then used to
determine the best node to schedule a pod on based on the pod's predicted power consumption and efficiency.

---

## Quick Start

### Prerequisites
- Python 3.10+
- Docker Desktop (installed and running)
- KinD CLI
- Kubernetes CLI
- Helm CLI

### 1. Clone & set up
```bash
git clone https://github.com/andrewauld/Zero-Scheduler.git 
cd Zero-Scheduler

# Create a virtual environment to handle necessary dependencies
python3 -m venv .venv
source .venv/bin/activate

# Create Docker images for the cluster services, repeat for each sub-directory
cd services/<sub-directory>
docker build -t kind.local/<service-name>:v1 .
```

### 2. Deploy the cluster
A convenience script is provided to set up the cluster in one of two modes:
- Using the Default Kubernetes scheduler
- Using the Zero Scheduler (ML extended scheduler)

To run the script, navigate to the project root and run:
```bash
# Using the default scheduler
./setup.sh

# Using the Zero Scheduler
./setup.sh true
```

This will set up a local KinD cluster with one control plane node and three worker nodes. It will also install
Prometheus and Grafana into the cluster (instructions on how to access these can be found in the script output).

Once the script has finished running, make sure to port-forward Kourier and Prometheus using the commands found at
the end of the script output.

### 3. Running the cluster workload
To run the simulated serverless workload, run:
```bash
python workload_generator.py
```

This will start a realistic serverless workload on the cluster, in which the services from the `services` directory
will be randomly scheduled on the cluster. The workload will run for 10 minutes, separated into 4 phases of 2 minutes,
3 minutes, 3 minutes, and 2 minutes, respectively.

During these phases, a ramp-up pattern is applied to the workload, consisting of 10 rq/s (requests per second) for the
first phase, 30 rq/s for the second phase, 50 rq/s for the third phase, and finally, 100 rq/s for the final phase. You
will receive a message in the terminal indicating the workload generator has finished when the 10 minutes have passed.

### 4. Collecting cluster data

`IMPORTANT:` First runs must be done with the default scheduler to collect data. This data can then be used
to train the ML models available in the `models` directory.

To collect cluster data, run:
```bash
# On experiment runs with the default scheduler
python metrics_scraper.py

# On experiment runs with the Zero Scheduler
python metrics_scraper.py ml
```

This will collect metrics from the cluster from a 14-minute window, and save them to a CSV file in the `data` directory.
Once you have completed your desired number of experiment runs, use the `combiner.py` script to combine the CSV files
into a single file:
```bash
python combiner.py
```

### 5. Training the ML models
To train the ML models, simply navigate to the `models` directory and run each of the files to train and export the 
models to a pickle file.

### 6. Final steps
Once you have completed the steps above, you can repeat steps 2 - 4 to run the workload on the cluster with the trained
Zero Scheduler.

### 7. Cleaning up
To delete the cluster and clean up the environment, simply run:
```bash
./cleanup.sh
```
from the project root.

---

## Project Structure

```
Zero-Scheduler/
├── README.md
├── cleanup.sh
├── combiner.py
├── compare.py
├── config.yaml
├── data/
│   ├── default/
│   └── ml/
├── extender/
│   ├── Dockerfile
│   ├── ml-extender-deployment.yaml
│   └── ml_extender.py
├── inject_flag.py
├── inject_mount.py
├── metrics_scraper.py
├── ml-scheduler-config.yaml
├── models/
│   ├── gradient_boosting.py
│   ├── random_forrest.py
│   └── support_vector.py
├── services/
│   ├── fanout/
│   │   ├── Dockerfile
│   │   ├── fanout_func.py
│   │   └── fanout_service.yaml
│   ├── matrix_multiplication/
│   │   ├── Dockerfile
│   │   ├── matrix_mult.py
│   │   └── matrix_service.yaml
│   ├── password_hashing/
│   │   ├── Dockerfile
│   │   ├── pass_hash.py
│   │   └── password_service.yaml
│   └── prime_factorisation/
│       ├── Dockerfile
│       ├── prime_fact.py
│       └── prime_service.yaml
├── setup.sh
└── workload_generator.py
```

