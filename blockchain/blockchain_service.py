import os
import json
import time
from web3 import Web3
from flask import current_app
from config import Config

class BlockchainConnectionError(Exception):
    """Custom exception raised when the blockchain network is unreachable."""
    pass

class BlockchainService:
    def __init__(self):
        self.rpc_url = Config.BLOCKCHAIN_RPC_URL
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.contract = None
        self.contract_address = None
        self.private_key = Config.OWNER_PRIVATE_KEY
        self._load_contract()

    def _load_contract(self):
        """Loads contract address and ABI from the JSON file generated during deployment."""
        if not os.path.exists(Config.CONTRACT_INFO_PATH):
            print(f"Contract info file not found at {Config.CONTRACT_INFO_PATH}")
            return
        
        try:
            with open(Config.CONTRACT_INFO_PATH, "r") as f:
                contract_info = json.load(f)
                self.contract_address = contract_info.get("address")
                self.contract_abi = contract_info.get("abi")
                
                if self.w3.is_connected() and self.contract_address:
                    self.contract = self.w3.eth.contract(
                        address=Web3.to_checksum_address(self.contract_address),
                        abi=self.contract_abi
                    )
        except Exception as e:
            print(f"Failed to load smart contract: {e}")

    def is_connected(self):
        """Checks if Web3 is connected to the Ethereum RPC endpoint."""
        try:
            return self.w3.is_connected()
        except Exception:
            return False

    def _get_contract(self):
        """Ensures the contract instance is loaded and connection is active."""
        if not self.is_connected():
            raise BlockchainConnectionError("Unable to connect to local blockchain network.")
        if not self.contract:
            self._load_contract()
            if not self.contract:
                raise BlockchainConnectionError("Smart contract not loaded. Run deployment first.")
        return self.contract

    def register_report(self, report_id, report_hash, lab_id):
        """
        Signs and submits a transaction to register a new report on-chain.
        Returns (tx_hash, block_number).
        """
        contract = self._get_contract()
        account = self.w3.eth.account.from_key(self.private_key)
        sender_address = account.address
        timestamp = int(time.time())

        # Build transaction
        tx = contract.functions.registerReport(
            report_id,
            report_hash,
            lab_id,
            timestamp
        ).build_transaction({
            'from': sender_address,
            'nonce': self.w3.eth.get_transaction_count(sender_address),
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price,
            'chainId': self.w3.eth.chain_id
        })

        # Sign and send transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash_bytes = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for receipt
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash_bytes)
        return receipt.transactionHash.hex(), receipt.blockNumber

    def update_report_version(self, report_id, new_hash):
        """
        Signs and submits a transaction to register a corrected report version on-chain.
        Returns (tx_hash, block_number).
        """
        contract = self._get_contract()
        account = self.w3.eth.account.from_key(self.private_key)
        sender_address = account.address
        timestamp = int(time.time())

        # Build transaction
        tx = contract.functions.updateReportVersion(
            report_id,
            new_hash,
            timestamp
        ).build_transaction({
            'from': sender_address,
            'nonce': self.w3.eth.get_transaction_count(sender_address),
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price,
            'chainId': self.w3.eth.chain_id
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash_bytes = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash_bytes)
        return receipt.transactionHash.hex(), receipt.blockNumber

    def revoke_report(self, report_id):
        """
        Signs and submits a transaction to revoke a report on-chain.
        Returns (tx_hash, block_number).
        """
        contract = self._get_contract()
        account = self.w3.eth.account.from_key(self.private_key)
        sender_address = account.address
        timestamp = int(time.time())

        # Build transaction
        tx = contract.functions.revokeReport(
            report_id,
            timestamp
        ).build_transaction({
            'from': sender_address,
            'nonce': self.w3.eth.get_transaction_count(sender_address),
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price,
            'chainId': self.w3.eth.chain_id
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash_bytes = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash_bytes)
        return receipt.transactionHash.hex(), receipt.blockNumber

    def get_report(self, report_id, version=0):
        """
        Retrieves a report's record from the blockchain.
        If version is 0, retrieves the current version.
        Returns a dict: {reportHash, labId, timestamp, version, status, exists}
        """
        contract = self._get_contract()
        try:
            res = contract.functions.getReport(report_id, version).call()
            # Returns (reportHash, labId, timestamp, version, status, exists)
            return {
                "reportHash": res[0],
                "labId": res[1],
                "timestamp": res[2],
                "version": res[3],
                "status": res[4],  # 0=ACTIVE, 1=SUPERSEDED, 2=REVOKED
                "exists": res[5]
            }
        except Exception as e:
            print(f"Error fetching report from blockchain: {e}")
            return None

    def get_latest_version(self, report_id):
        """Gets the latest version number of a report on-chain."""
        contract = self._get_contract()
        try:
            return contract.functions.getLatestVersion(report_id).call()
        except Exception:
            return 0

    def get_block_info(self, block_number):
        """Retrieves block information by number."""
        if not self.is_connected():
            raise BlockchainConnectionError("Unable to connect to local blockchain network.")
        try:
            block = self.w3.eth.get_block(block_number)
            return {
                "number": block.number,
                "hash": block.hash.hex(),
                "parentHash": block.parentHash.hex(),
                "timestamp": block.timestamp,
                "difficulty": block.difficulty,
                "size": block.size
            }
        except Exception as e:
            print(f"Error fetching block info: {e}")
            return None

    def get_transaction_info(self, tx_hash):
        """Retrieves transaction and receipt details by transaction hash."""
        if not self.is_connected():
            raise BlockchainConnectionError("Unable to connect to local blockchain network.")
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return {
                "hash": tx.hash.hex(),
                "blockNumber": tx.blockNumber,
                "blockHash": tx.blockHash.hex(),
                "from": tx['from'],
                "to": tx['to'],
                "gasUsed": receipt.gasUsed,
                "status": receipt.status,
                "gasPrice": tx.gasPrice
            }
        except Exception as e:
            print(f"Error fetching transaction info: {e}")
            return None

    def get_latest_block_number(self):
        """Retrieves the current block number on the local blockchain."""
        if not self.is_connected():
            return 0
        try:
            return self.w3.eth.block_number
        except Exception:
            return 0
