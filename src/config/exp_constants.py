from src.experiments.matrix_size import MatrixSizeExperiment
from src.experiments.matrix_density import MatrixDensityExperiment
from src.experiments.arweave_experiment import ARWeaveExperiment
from src.experiments.s3_experiment import S3Experiment
from src.experiments.server_experiment import ServerBasedExperiment
from src.experiments.consistent_hashing_experiment import ConsistentHashExp

EXP_FLAGS = {
    # Start from a small matrix size NxM and increase by K across both dimensions, and then across each dimension
    # individually. This results in a benchmark that reveals how much time a multiplication takes based on it's size,
    # and how well it scales This is almost always memory bound, and the experiment is run on various hardware to find
    # baselines for CPU and RAM size
    'MATRIX_SIZE_FINDER_EXP': MatrixSizeExperiment(),

    # Benchmarks a series of pre-generated matrices. Multiplies them and gradually increases sparsity
    # to verify impact. The pre-generated matrices are 700GB worth of exercises: 3 different ranges of numbers
    # with 10 exercises for each.
    'MATRIX_DENSITY_EXP': MatrixDensityExperiment(),

    # Benchmarks a series of upload operations to verify AR network latency across time. This uses different file
    # sizes, and must have the key to a wallet with AR funds
    'AR_UPLOAD_EXP': ARWeaveExperiment(True),

    # Similar to AR_UPLOAD_EXP, but benchmarks downloads of known, previously uploaded exercises. This will therefore
    # use a cache that's constantly updated with exercises uploaded by AR_UPLOAD_EXP, or manually.
    'AR_DOWNLOAD_EXP': ARWeaveExperiment(False),

    # Same as AR_UPLOAD_EXP, but using S3
    'S3_UPLOAD_EXP': S3Experiment(True),

    # Same as AR_DOWNLOAD_EXP, but using S3
    'S3_DOWNLOAD_EXP': S3Experiment(False),

    # Same as PEERCONNECT_RECV, but benchmarks running a series of sample network transactions to benchmark peer to peer
    # latency.
    'PEERCONNECT_SEND': ServerBasedExperiment(False),

    # Waits for valid PoX messages from any address, benchmarking wait times. This is used to estimate network
    # overhead, and potential blockers in the communication protocol with respect to PoX efficiency
    'PEERCONNECT_RECV': ServerBasedExperiment(True),

    # Various experiments based on the consistent hashing methods used in the PoUW protocol. Computes the network node
    # distribution when selecting exercises to solve, to validate, and other network parameters.
    'CONSISTENT_HASH': ConsistentHashExp()
}
