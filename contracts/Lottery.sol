// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
// https://docs.openzeppelin.com/contracts/4.x/access-control
// https://github.com/OpenZeppelin/openzeppelin-contracts
import "@openzeppelin/contracts/access/Ownable.sol"; //onlyOwner modifier
// random number
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

// Ownable comes from openzeppelin
contract Lottery is VRFConsumerBase, Ownable {
    // keep track of all the players who have payed
    address payable[] public players;
    address payable public recentWinner;
    // keeyp track of recent number
    uint256 public randomness;
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

    // to use the VRFConsumer we need to pay a fee
    // can change from block chain to block chain
    uint256 public fee;
    // way to uniquely identify chainlink vrf node
    bytes32 keyhash;

    // event piece of data executed in blockchain 
    // store in blockchain but not accessible
    // printline of blockchain
    // SMART CONTRACT CANT access evemts
    event RequestedRandomness(bytes32 requestId);



    // to pass the address to Aggregator to find
    // eth/usd
    // add another constructor to our constructor
    constructor(address _priceFeedAddress, address _vrfCoordinator, address _link, uint256 _fee, bytes32 _keyhash) public VRFConsumerBase(
        _vrfCoordinator,
        _link
    ) {
        // unit in wey
        // need a price feed to transform
        // https://docs.chain.link/docs/get-the-latest-price/
        usdEntryFee = 50 * (10 ** 18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        // when we start the lottery will be closed
        lottery_state = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyhash = _keyhash;
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
        uint256 adjustedPrice = uint256(price); //  * (10**10); // 18 decimal
        uint256 costToEnter = (usdEntryFee * (10**18)) / adjustedPrice;
        return costToEnter;
    }

    // need to be called only by our admin
    function startLottery() public onlyOwner {
        require(lottery_state == LOTTERY_STATE.CLOSED, "Can\'t start new lottery yet");
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner  {
        // do NOT USE IN PRODUCTION to generate pseudo randmoness
        // hashing function is not random
        // nonce // nonce is predictable (transaction number)
        // block.difficulty // can be manipulated by minner
        // uint256(keccak256(abi.encodePacked(nonce, msg.sender, block.difficulty,block.timestamp))) % player.length;
        

        // we are going to use : https://docs.chain.link/docs/chainlink-vrf/
        // we change state calculating winner
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        // import from VRFConsumerBase // https://docs.chain.link/docs/get-a-random-number/
        // https://github.com/smartcontractkit/chainlink-mix/blob/master/contracts/VRFConsumer.sol
        // requestRandomness() Follow Request Response pattern 
        // request the data in second callback the chainlink node
        // will return data to another function call fullfillrandomness
        bytes32 requestId = requestRandomness(keyhash, fee);

        // We want to emit event 
        emit RequestedRandomness(requestId);
    }

    // 1 - Stop the lottery then request random number
    // 2 - Once the chainlink has a random number we call a second transaction
    // no body can call this function so only the VRF Coordinator
    function fulfillRandomness(bytes32 _requestId, uint256 _randomness) internal override {
        // make sure we are in the right state
        require(lottery_state == LOTTERY_STATE.CALCULATING_WINNER, "You aren't there yet.");
        // make sure we have a random number
        require(_randomness > 0, "random-not-found");
        // need to choose a winner 
        // 7 players but random num = 22
        // 22 % 7  = 3
        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];
        // now we have winner we can pay them 
        recentWinner.transfer(address(this).balance);
        // Reset the lottery
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }

}