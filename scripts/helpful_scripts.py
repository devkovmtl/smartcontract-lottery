from brownie import network, accounts, config

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-for-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


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
