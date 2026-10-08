import os
import hashlib
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

CONTRACT_ABI = [
    {"inputs":[],"stateMutability":"nonpayable","type":"constructor"},
    {"anonymous":False,"inputs":[{"indexed":True,"internalType":"bytes32","name":"hash","type":"bytes32"},{"indexed":False,"internalType":"uint256","name":"timestamp","type":"uint256"},{"indexed":True,"internalType":"address","name":"issuer","type":"address"}],"name":"DiplomaRegistered","type":"event"},
    {"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"bytes32","name":"hash","type":"bytes32"}],"name":"registerDiploma","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"bytes32","name":"hash","type":"bytes32"}],"name":"verifyDiploma","outputs":[{"internalType":"bool","name":"exists","type":"bool"},{"internalType":"uint256","name":"timestamp","type":"uint256"},{"internalType":"address","name":"issuer","type":"address"}],"stateMutability":"view","type":"function"}
]


def get_web3():
    api_key = os.getenv("API_KEY")
    alchemy_url = "https://eth-sepolia.g.alchemy.com/v2/" + api_key
    return Web3(Web3.HTTPProvider(alchemy_url))


def get_contract(w3=None):
    if w3 is None:
        w3 = get_web3()
    contract_address = os.getenv("CONTRACT_ID")
    return w3.eth.contract(
        address=Web3.to_checksum_address(contract_address),
        abi=CONTRACT_ABI
    )


def register_hash(hash_hex):
    private_key = os.getenv("PRIVATE_KEY")
    w3 = get_web3()
    contract = get_contract(w3)
    account = w3.eth.account.from_key(private_key)

    hash_bytes32 = bytes.fromhex(hash_hex)

    tx = contract.functions.registerDiploma(hash_bytes32).build_transaction({
        "chainId": 11155111,
        "from": account.address,
        "gasPrice": w3.eth.gas_price,
        "nonce": w3.eth.get_transaction_count(account.address),
    })
    tx["gas"] = w3.eth.estimate_gas(tx)

    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return tx_hash.hex(), receipt.blockNumber


def verify_hash(hash_hex):
    w3 = get_web3()
    contract = get_contract(w3)

    hash_bytes32 = bytes.fromhex(hash_hex)
    exists, timestamp, issuer = contract.functions.verifyDiploma(hash_bytes32).call()

    return exists, timestamp, issuer
