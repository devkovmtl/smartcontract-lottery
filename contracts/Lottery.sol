// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
// https://docs.openzeppelin.com/contracts/4.x/access-control
// https://github.com/OpenZeppelin/openzeppelin-contracts
import "@openzeppelin/contracts/access/Ownable.sol"; //onlyOwner modifier

// Ownable comes from openzeppelin
contract Lottery is Ownable {
    // keep track of all the players who have payed
    address payable[] public players;
    // minimum of entry fee
    uint256 public usdEntryFee;
    // Store our price feed
    AggregatorV3Interface internal ethUsdPriceFeed;
    // our enum to make track state of lottery, start, end...
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    // track state
    LOTTERY_STATE public lottery_state;


    // to pass the address to Aggregator to find
    // eth/usd
    constructor(address _priceFeedAddress) {
        // unit in wey
        // need a price feed to transform
        // https://docs.chain.link/docs/get-the-latest-price/
        usdEntryFee = 50 * (10 ** 18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        // when we start the lottery will be closed
        lottery_state = LOTTERY_STATE.CLOSED;
    }
 
    // we need user to pay so make the function 
    // payable
    function enter() public payable {
        require(lottery_state == LOTTERY_STATE.OPEN);
        // Check a minimum of $50
        require(msg.value >= getEntranceFee(), "Not enough eth");
        // each time somebody pay keep track
        players.push(payable(msg.sender));
    }

    // we return just a number view 
    // need a price feed to transform 50USD to ETH
    // https://docs.chain.link/docs/get-the-latest-price/
    // https://docs.chain.link/docs/ethereum-addresses/
    function getEntranceFee() public view returns (uint256) {
        // dont need the rest of variable 
        (,int price,,,) = ethUsdPriceFeed.latestRoundData();
        // $50, $2000 /ETH
        // 50/2000 (solidity dont work with big number)
        // 50 * 1000 /2000
        // we receive 8 decimal * 10**10 we have 18 decimal
        uint256 adjustedPrice = uint256(price) * 10 ** 10; // 18 decimal
        uint256 costToEnter = (usdEntryFee * 10 ** 18) / adjustedPrice;
        return costToEnter;
    }

    // need to be called only by our admin
    function startLottery() public onlyOwner {
        require(lottery_state == LOTTERY_STATE.CLOSED, "Can\'t start new lottery yet");
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner  {}

}