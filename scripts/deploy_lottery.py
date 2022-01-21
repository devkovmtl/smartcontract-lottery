from brownie import Lottery, config, network
from scripts.helpful_scripts import get_account, get_contract, fun_with_link
import time


def deploy_lottery():
    account = get_account()
    #  Our lottery has constructor args:
    # address _priceFeedAddress, address _vrfCoordinator, address _link, uint256 _fee, bytes32 _keyhash
    # if we are not on chain we need to deploy our mocks
    # we pass contract_name from our brownie config file
    # from the name we get the type contract
    Lottery.deploy(
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


def start_lottery():
    account = get_account()
    # grab last contract
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("The lottery is started")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # need to send some entrance fee
    value = lottery.getEntranceFee()
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("You entered the lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # we need LINK Token to be able to call the get requestRandomness
    # fund the contract
    # end the lottery
    tx = fun_with_link(lottery.address)
    tx.wait(1)
    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    # need to wait for the callback from chainlink
    time.sleep(60)
    # we can see who is winner
    print(f"{lottery.recentWinner} is the new winner!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
