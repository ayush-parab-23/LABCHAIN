import hashlib

def calculate_sha256(file_path):
    """
    Calculates the SHA-256 hash of a file by reading it in binary mode.
    This creates a cryptographic fingerprint of the report.
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash in chunks of 4K to prevent high memory usage
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
