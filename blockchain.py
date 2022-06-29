import hashlib
import datetime
import json
from flask import Flask, jsonify

#part1: Building a blockchain
class Blockchain: 
  def __init__(self):
    self.chain= [] #a list of block
    self.create_block(proof=1,previous_hash='0')  #genesis block--> The first block of blockchain 
  def create_block(self,proof,previous_hash):
    block= {
      "index": len(self.chain) + 1,
      "timestamp": str(datetime.datetime.now()),
      "proof": proof,
      "previous_hash": previous_hash
    }
    self.chain.append(block)
    return block
  def get_previous_block(self):
    return self.chain[-1]  
  def proof_of_work(self,previous_proof):
    new_proof= 1
    check_proof= False
    while check_proof is False:
      #if 4 leading char of this operation are zeroes then miner wins (cryptographic hash starting with four zeroes)
      #learn more about hash_operation how to create more complex hash operation
      hash_operation= hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
      if(hash_operation[:4]=="0000"):
        check_proof= True
      else: 
        new_proof+= 1
    return new_proof   

#part2 mining our blockchain