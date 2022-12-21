// SPDX-License-Identifier: CC-BY-SA-4.0
pragma solidity >= 0.5.0 < 0.9.0;

contract sendPairingElement {

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

  function setAuthoritiesNames(address _address, uint64 _instanceID, bytes32 _hash1, bytes32 _hash2) public {
    authoritiesName[_instanceID][_address].hashPart1 = _hash1;
    authoritiesName[_instanceID][_address].hashPart2 = _hash2;
  }

  function getAuthoritiesNames(address _address, uint64 _instanceID) public view returns (bytes memory) {
    bytes32 p1 = authoritiesName[_instanceID][_address].hashPart1;
    bytes32 p2 = authoritiesName[_instanceID][_address].hashPart2;
    bytes memory joined = new bytes(64);
    assembly {
      mstore(add(joined, 32), p1)
      mstore(add(joined, 64), p2)
    }
    return joined;
  }

  function setElementHashed(address _address, uint64 _instanceID, bytes32 _hash1, bytes32 _hash2, bytes32 _hash3, bytes32 _hash4) public {
    firstGHashed[_instanceID][_address].hashPart1 = _hash1;
    firstGHashed[_instanceID][_address].hashPart2 = _hash2;
    secondGHashed[_instanceID][_address].hashPart1 = _hash3;
    secondGHashed[_instanceID][_address].hashPart2 = _hash4;
  }

  function getElementHashed(address _address, uint64 _instanceID) public view returns (bytes memory, bytes memory) {
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

  function setElement(address _address, uint64 _instanceID, bytes32 _hash1, bytes32 _hash2, bytes32 _hash3, bytes32 _hash4, bytes32 _hash5, bytes32 _hash6) public {
    firstG[_instanceID][_address].hashPart1 = _hash1;
    firstG[_instanceID][_address].hashPart2 = _hash2;
    firstG[_instanceID][_address].hashPart3 = _hash3;
    secondG[_instanceID][_address].hashPart1 = _hash4;
    secondG[_instanceID][_address].hashPart2 = _hash5;
    secondG[_instanceID][_address].hashPart3 = _hash6;
  }

  function getElement(address _address, uint64 _instanceID) public view returns (bytes memory, bytes32, bytes memory, bytes32) {
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

  function setPublicParameters(address _address, uint64 _instanceID, bytes32 _hash1, bytes32 _hash2) public {
    parameters[_instanceID][_address].hashPart1 = _hash1;
    parameters[_instanceID][_address].hashPart2 = _hash2;
  }

  function getPublicParameters(address _address, uint64 _instanceID) public view returns (bytes memory) {
    bytes32 p1 = parameters[_instanceID][_address].hashPart1;
    bytes32 p2 = parameters[_instanceID][_address].hashPart2;
    bytes memory joined = new bytes(64);
    assembly {
      mstore(add(joined, 32), p1)
      mstore(add(joined, 64), p2)
    }
    return joined;
  }

}
