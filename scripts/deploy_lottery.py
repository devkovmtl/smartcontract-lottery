from brownie import Lottery, config, network
from scripts.helpful_scripts import get_account, get_contract


def deploy_lottery():
    account = get_account()
    #  Our lottery has constructor args:
    # address _priceFeedAddress, address _vrfCoordinator, address _link, uint256 _fee, bytes32 _keyhash
    # if we are not on chain we need to deploy our mocks
    # we pass contract_name from our brownie config file
    # from the name we get the type contract
    lottery = Lottery.deploy(
        # price_feed address
        get_contract("eth_usd_price_feed").address,
        # vrfCoordinator address
        get_contract("vrf_coordinator").address,
        # link token another smart contract
        get_contract("link_token").address,
        # fee and keyhash just number
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Deployed Lottery!")


def main():
    deploy_lottery()
