
pragma solidity ^0.8.19;

contract DiplomaRegistry {
    address public owner;

    struct DiplomaRecord {
        bool exists;
        uint256 timestamp;
        address issuer;
    }

    mapping(bytes32 => DiplomaRecord) public diplomas;

    event DiplomaRegistered(bytes32 indexed hash, uint256 timestamp, address indexed issuer);

    constructor() {
        owner = msg.sender;
    }

    function registerDiploma(bytes32 hash) external {
        require(!diplomas[hash].exists, "Hash already registered");
        diplomas[hash] = DiplomaRecord(true, block.timestamp, msg.sender);
        emit DiplomaRegistered(hash, block.timestamp, msg.sender);
    }

    function verifyDiploma(bytes32 hash) external view returns (bool, uint256, address) {
        DiplomaRecord memory record = diplomas[hash];
        return (record.exists, record.timestamp, record.issuer);
    }
}
