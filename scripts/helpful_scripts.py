from brownie import MockV3Aggregator, network, accounts, config, Contract
from web3 import Web3

# dont need to deploy a mock price feed on fork local
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-for-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


DECIMALS = 18
INITIAL_VALUE = Web3.toWei(2000, "ether")


# def get_account():
#     # Etheir we use ganache local accounts
#     # Or we use .env
#     if (
#         network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
#         or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
#     ):
#         return accounts[0]
#     else:
#         return accounts.add(config["wallets"]["from_key"])

# Use accounts.load("id")
# id brownie accounts list
def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


# mapping to contract_name => type_of_contract
contract_to_mock = {"eth_usd_price_feed": MockV3Aggregator}

# get contract already deploy mock or real contract
# check if we are on chain or not
# if not we need to pass our mock
# from the name pass we will know type of contract
def get_contract(contract_name):
    """This function will grab the contract addresses from the brownie config
    if defined, otherwise, it will deploy a mock version of that contract, otherwise  return that mock contract.

        Args:
            contract_name (string)

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed version of this contract.
    """
    contract_type = contract_to_mock[contract_name]
    # check if we have to deploy a mock
    # work for our development
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        # check to see if contract already deploy
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]  # same MockV3Aggregator[-1]
    # to deploy to testnet
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # we need to get the address, ABI
        # get a contract with abi and address
        # MockV3Aggregator.abi, MockV3Aggregator._name
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


# Deploy mock v3
def deploy_mocks():
    print(f"The active network is {network.show_active()}")
    print("Deploying mocks...")
    account = get_account()
    mock_price_feed = MockV3Aggregator.deploy(
        DECIMALS, INITIAL_VALUE, {"from": account}
    )
    print("Mocks deployed!")
