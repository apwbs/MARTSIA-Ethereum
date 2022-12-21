// SPDX-License-Identifier: CC-BY-SA-4.0
pragma solidity >= 0.5.0 < 0.9.0;

contract messageExchange {

  struct publicKey {
    bytes32 hashPart1;
    bytes32 hashPart2;
  }
  mapping (uint64 => mapping (address =>  publicKey)) publicKeys;

  struct IPFSCiphertext {
    bytes32 hashPart1;
    bytes32 hashPart2;
  }
  mapping (uint64 => IPFSCiphertext) allLinks;

  struct userAttributes {
    bytes32 hashPart1;
    bytes32 hashPart2;
  }
  mapping (uint64 => userAttributes) allUsers;

  function setPublicKey(address _address, uint64 _instanceID, bytes32 _hash1, bytes32 _hash2) public {
    publicKeys[_instanceID][_address].hashPart1 = _hash1;
    publicKeys[_instanceID][_address].hashPart2 = _hash2;
  }

  function getPublicKey(address _address, uint64 _instanceID) public view returns (bytes memory) {
    bytes32 p2 = publicKeys[_instanceID][_address].hashPart1;
    bytes32 p3 = publicKeys[_instanceID][_address].hashPart2;
    bytes memory joined = new bytes(64);
    assembly {
      mstore(add(joined, 32), p2)
      mstore(add(joined, 64), p3)
    }
      return (joined);
  }

  function setIPFSLink(uint64 _messageID, bytes32 _hash1, bytes32 _hash2) public {
    allLinks[_messageID].hashPart1 = _hash1;
    allLinks[_messageID].hashPart2 = _hash2;
  }

  function getIPFSLink(uint64 _messageID) public view returns (bytes memory) {
    bytes32 p1 = allLinks[_messageID].hashPart1;
    bytes32 p2 = allLinks[_messageID].hashPart2;
    bytes memory joined = new bytes(64);
    assembly {
      mstore(add(joined, 32), p1)
      mstore(add(joined, 64), p2)
    }
    return joined;
  }

  function setUserAttributes(uint64 _instanceID, bytes32 _hash1, bytes32 _hash2) public {
    allUsers[_instanceID].hashPart1 = _hash1;
    allUsers[_instanceID].hashPart2 = _hash2;
  }

  function getUserAttributes(uint64 _instanceID) public view returns (bytes memory) {
    bytes32 p1 = allUsers[_instanceID].hashPart1;
    bytes32 p2 = allUsers[_instanceID].hashPart2;
    bytes memory joined = new bytes(64);
    assembly {
      mstore(add(joined, 32), p1)
      mstore(add(joined, 64), p2)
    }
    return joined;
  }

}
