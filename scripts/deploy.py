from brownie import Lottery
from scripts.helpful_scripts import get_account, get_contract


def deploy_lottery():
    account = get_account()
    #  Our lottery has constructor args:
    # address _priceFeedAddress, address _vrfCoordinator, address _link, uint256 _fee, bytes32 _keyhash
    # if we are not on chain we need to deploy our mocks
    # we pass contract_name from our brownie config file 
    # from the name we get the type contract
    lottery = Lottery.deploy(get_contract("eth_usd_price_feed"), {"from":account})


def main():
    deploy_lottery()
