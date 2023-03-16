// SPDX-License-Identifier: CC-BY-SA-4.0
pragma solidity >= 0.5.0 < 0.9.0;

contract MARTSIAEth {

  uint public AUTH = 0;
  uint public AUTHDESTRUCTION = 0;
  address payable public address_to_pay;
  address[3] public attributeCertifiers=[0xE594fDE847c1ab4622a6c4B961c87BaC294A4498, 0x4F16A60a4181BF33216864acCFdFd61ba82A2Aa1, 0x84e83824a78cEAE16C6ED8b4EE2cD55FE648f864];
  mapping (address => bool) public userAddr;
  mapping (address => bool) public userAddrDest;


  constructor() payable {
    address_to_pay = payable(msg.sender);
  }

  function updateMajorityCount() public {
    for (uint j = 0; j < attributeCertifiers.length; j++) {
      if (msg.sender == attributeCertifiers[j]){
        AUTH = AUTH + 1;
        userAddr[msg.sender] = true;
      }
    }
  }

  modifier Majority() {
    require(AUTH > (uint(attributeCertifiers.length) * 2 / 3), "No action possible without the majority");
    _;
  }

  struct authoritiesNames {
    bytes32 hashPart1;
    bytes32 hashPart2;
  }
  mapping (uint64 => mapping (address => authoritiesNames)) authoritiesName;

  struct firstElementHashed {
    bytes32 hashPart1;
    bytes32 hashPart2;
  }
  mapping (uint64 => mapping (address => firstElementHashed)) firstGHashed;

  struct secondElementHashed {
    bytes32 hashPart1;
    bytes32 hashPart2;
  }
  mapping (uint64 => mapping (address => secondElementHashed)) secondGHashed;

  struct firstElement {
    bytes32 hashPart1;
    bytes32 hashPart2;
    bytes32 hashPart3;
  }
  mapping (uint64 => mapping (address => firstElement)) firstG;

  struct secondElement {
    bytes32 hashPart1;
    bytes32 hashPart2;
    bytes32 hashPart3;
  }
  mapping (uint64 => mapping (address => secondElement)) secondG;

  struct publicParameters {
    bytes32 hashPart1;
    bytes32 hashPart2;
  }
  mapping (uint64 => mapping (address => publicParameters)) parameters;

  struct publicKey {
    bytes32 hashPart1;
    bytes32 hashPart2;
  }
  mapping (uint64 => mapping (address =>  publicKey)) publicKeys;

  struct publicKeyReaders {
    bytes32 hashPart1;
    bytes32 hashPart2;
  }
  mapping (address =>  publicKeyReaders) publicKeysReaders;

  struct IPFSCiphertext {
    address sender;
    bytes32 hashPart1;
    bytes32 hashPart2;
  }
  mapping (uint64 => IPFSCiphertext) allLinks;

  struct userAttributes {
    bytes32 hashPart1;
    bytes32 hashPart2;
  }
  mapping (uint64 => userAttributes) allUsers;

  function setAuthoritiesNames(uint64 _instanceID, bytes32 _hash1, bytes32 _hash2) public Majority {
    authoritiesName[_instanceID][msg.sender].hashPart1 = _hash1;
    authoritiesName[_instanceID][msg.sender].hashPart2 = _hash2;
  }

  function getAuthoritiesNames(address _address, uint64 _instanceID) public view Majority returns (bytes memory) {
    bytes32 p1 = authoritiesName[_instanceID][_address].hashPart1;
    bytes32 p2 = authoritiesName[_instanceID][_address].hashPart2;
    bytes memory joined = new bytes(64);
    assembly {
      mstore(add(joined, 32), p1)
      mstore(add(joined, 64), p2)
    }
    return joined;
  }

  function setElementHashed(uint64 _instanceID, bytes32 _hash1, bytes32 _hash2, bytes32 _hash3, bytes32 _hash4) public Majority {
    firstGHashed[_instanceID][msg.sender].hashPart1 = _hash1;
    firstGHashed[_instanceID][msg.sender].hashPart2 = _hash2;
    secondGHashed[_instanceID][msg.sender].hashPart1 = _hash3;
    secondGHashed[_instanceID][msg.sender].hashPart2 = _hash4;
  }

  function getElementHashed(address _address, uint64 _instanceID) public view Majority returns (bytes memory, bytes memory) {
    bytes32 p1 = firstGHashed[_instanceID][_address].hashPart1;
    bytes32 p2 = firstGHashed[_instanceID][_address].hashPart2;
    bytes32 p3 = secondGHashed[_instanceID][_address].hashPart1;
    bytes32 p4 = secondGHashed[_instanceID][_address].hashPart2;
    bytes memory joined = new bytes(64);
    assembly {
      mstore(add(joined, 32), p1)
      mstore(add(joined, 64), p2)
    }
    bytes memory joinedsec = new bytes(64);
    assembly {
      mstore(add(joinedsec, 32), p3)
      mstore(add(joinedsec, 64), p4)
    }
    return (joined, joinedsec);
  }

  function setElement(uint64 _instanceID, bytes32 _hash1, bytes32 _hash2, bytes32 _hash3, bytes32 _hash4, bytes32 _hash5, bytes32 _hash6) public Majority {
    firstG[_instanceID][msg.sender].hashPart1 = _hash1;
    firstG[_instanceID][msg.sender].hashPart2 = _hash2;
    firstG[_instanceID][msg.sender].hashPart3 = _hash3;
    secondG[_instanceID][msg.sender].hashPart1 = _hash4;
    secondG[_instanceID][msg.sender].hashPart2 = _hash5;
    secondG[_instanceID][msg.sender].hashPart3 = _hash6;
  }

  function getElement(address _address, uint64 _instanceID) public view Majority returns (bytes memory, bytes32, bytes memory, bytes32) {
    bytes32 p1 = firstG[_instanceID][_address].hashPart1;
    bytes32 p2 = firstG[_instanceID][_address].hashPart2;
    bytes32 p3 = firstG[_instanceID][_address].hashPart3;
    bytes32 p4 = secondG[_instanceID][_address].hashPart1;
    bytes32 p5 = secondG[_instanceID][_address].hashPart2;
    bytes32 p6 = secondG[_instanceID][_address].hashPart3;
    bytes memory joined = new bytes(64);
    assembly {
      mstore(add(joined, 32), p1)
      mstore(add(joined, 64), p2)
    }
    bytes memory joinedsec = new bytes(64);
    assembly {
      mstore(add(joinedsec, 32), p4)
      mstore(add(joinedsec, 64), p5)
    }

    return (joined, p3, joinedsec, p6);
  }

  function setPublicParameters(uint64 _instanceID, bytes32 _hash1, bytes32 _hash2) public Majority {
    parameters[_instanceID][msg.sender].hashPart1 = _hash1;
    parameters[_instanceID][msg.sender].hashPart2 = _hash2;
  }

  function getPublicParameters(address _address, uint64 _instanceID) public view Majority returns (bytes memory) {
    bytes32 p1 = parameters[_instanceID][_address].hashPart1;
    bytes32 p2 = parameters[_instanceID][_address].hashPart2;
    bytes memory joined = new bytes(64);
    assembly {
      mstore(add(joined, 32), p1)
      mstore(add(joined, 64), p2)
    }
    return joined;
  }

  function setPublicKey(uint64 _instanceID, bytes32 _hash1, bytes32 _hash2) public Majority {
    publicKeys[_instanceID][msg.sender].hashPart1 = _hash1;
    publicKeys[_instanceID][msg.sender].hashPart2 = _hash2;
  }

  function getPublicKey(address _address, uint64 _instanceID) public view Majority returns (bytes memory) {
    bytes32 p2 = publicKeys[_instanceID][_address].hashPart1;
    bytes32 p3 = publicKeys[_instanceID][_address].hashPart2;
    bytes memory joined = new bytes(64);
    assembly {
      mstore(add(joined, 32), p2)
      mstore(add(joined, 64), p3)
    }
    return (joined);
  }

  function setPublicKeyReaders(bytes32 _hash1, bytes32 _hash2) public Majority {
    publicKeysReaders[msg.sender].hashPart1 = _hash1;
    publicKeysReaders[msg.sender].hashPart2 = _hash2;
  }

  function getPublicKeyReaders(address _address) public view Majority returns (bytes memory) {
    bytes32 p2 = publicKeysReaders[_address].hashPart1;
    bytes32 p3 = publicKeysReaders[_address].hashPart2;
    bytes memory joined = new bytes(64);
    assembly {
      mstore(add(joined, 32), p2)
      mstore(add(joined, 64), p3)
    }
    return (joined);
  }

  function setIPFSLink(uint64 _messageID, bytes32 _hash1, bytes32 _hash2) public Majority {
    allLinks[_messageID].sender = msg.sender;
    allLinks[_messageID].hashPart1 = _hash1;
    allLinks[_messageID].hashPart2 = _hash2;
  }

  function getIPFSLink(uint64 _messageID) public view Majority returns (address, bytes memory) {
    address sender = allLinks[_messageID].sender;
    bytes32 p1 = allLinks[_messageID].hashPart1;
    bytes32 p2 = allLinks[_messageID].hashPart2;
    bytes memory joined = new bytes(64);
    assembly {
      mstore(add(joined, 32), p1)
      mstore(add(joined, 64), p2)
    }
    return (sender, joined);
  }

  function setUserAttributes(uint64 _instanceID, bytes32 _hash1, bytes32 _hash2) public Majority {
    allUsers[_instanceID].hashPart1 = _hash1;
    allUsers[_instanceID].hashPart2 = _hash2;
  }

  function getUserAttributes(uint64 _instanceID) public view Majority returns (bytes memory) {
    bytes32 p1 = allUsers[_instanceID].hashPart1;
    bytes32 p2 = allUsers[_instanceID].hashPart2;
    bytes memory joined = new bytes(64);
    assembly {
      mstore(add(joined, 32), p1)
      mstore(add(joined, 64), p2)
    }
    return joined;
  }

  function dissolve() public {
    for (uint j = 0; j < attributeCertifiers.length; j++) {
      if (msg.sender == attributeCertifiers[j]){
        AUTHDESTRUCTION = AUTHDESTRUCTION + 1;
        userAddrDest[msg.sender] = true;
      }
    }
    if (AUTHDESTRUCTION > 1) {
      selfdestruct(address_to_pay);
    }
  }

}
