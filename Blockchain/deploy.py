import os
import json
from web3 import Web3
from dotenv import load_dotenv
from solcx import compile_source, install_solc

load_dotenv()

SOLC_VERSION = "0.8.19"

CONTRACT_SOURCE_PATH = os.path.join(os.path.dirname(__file__), "DiplomaRegistry.sol")

API_KEY = os.getenv("API_KEY")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

CHAIN_ID = 11155111


def get_web3():
    alchemy_url = "https://eth-sepolia.g.alchemy.com/v2/" + API_KEY
    return Web3(Web3.HTTPProvider(alchemy_url))


def compile_contract():
    install_solc(SOLC_VERSION)
    with open(CONTRACT_SOURCE_PATH, "r") as f:
        contract_source = f.read()
    compiled_sol = compile_source(contract_source, solc_version=SOLC_VERSION)
    contract_interface = compiled_sol.get(
        f"<stdin>:DiplomaRegistry"
    )
    return contract_interface


def deploy_contract():
    w3 = get_web3()
    assert w3.is_connected(), "Failed to connect to Alchemy"

    account = w3.eth.account.from_key(PRIVATE_KEY)
    w3.eth.default_account = account.address

    contract_interface = compile_contract()

    bytecode = contract_interface["bin"]
    abi = contract_interface["abi"]

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    nonce = w3.eth.get_transaction_count(account.address)

    transaction = contract.constructor().build_transaction({
        "chainId": CHAIN_ID,
        "gasPrice": w3.eth.gas_price,
        "nonce": nonce,
    })

    signed_tx = account.sign_transaction(transaction)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"Transaction hash: {tx_hash.hex()}")

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = receipt.contractAddress

    print(f"Contract deployed at: {contract_address}")

    contract_address_env = os.getenv("CONTRACT_ID")
    if contract_address_env != contract_address:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        with open(env_path, "r") as f:
            env_content = f.read()
        if "CONTRACT_ID" in env_content:
            import re
            env_content = re.sub(
                r"CONTRACT_ID=.*", f"CONTRACT_ID={contract_address}", env_content
            )
        else:
            env_content = env_content.strip() + f"\nCONTRACT_ID={contract_address}\n"
        with open(env_path, "w") as f:
            f.write(env_content)
        print("CONTRACT_ID updated in .env")

    return contract_address


if __name__ == "__main__":
    deploy_contract()
