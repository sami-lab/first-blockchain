import hashlib
import datetime
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

#part1: Building a blockchain
class Blockchain: 
  def __init__(self):
    self.chain= [] #a list of block
    self.transactions= [] #a list of transactions
    self.create_block(proof=1,previous_hash='0')  #genesis block--> The first block of blockchain 
    self.nodes= set() #nodes are systems running on internet and it always unique. 
  def create_block(self,proof,previous_hash):
    block= {
      "index": len(self.chain) + 1,
      "timestamp": str(datetime.datetime.now()),
      "proof": proof,
      "previous_hash": previous_hash,
      "transactions": self.transactions
    }
    self.transactions= []
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
   
   #this function return cryptographic hash of the block of our blockchain
  def hash(self,block):
     #.encode is require by hashlib256 which accept string in encoded format
     #hexdigest give hexadecimal format
     encoded_block= json.dumps(block,sort_keys=True).encode()
     return hashlib.sha256(encoded_block).hexdigest()
  def is_chain_valid(self,chain):
     previews_block = chain[0]
     block_index= 1   
     while (block_index< len(chain)):
       block = chain[block_index]
       #if previous block hash does match with current block previous_hash then chain is valid
       if( block["previous_hash"]!= self.hash(previews_block) ):
        return False
       previews_proof = previews_block["proof"]
       proof = block["proof"]
       hash_operation= hashlib.sha256(str(previews_proof**2 - proof**2).encode()).hexdigest()
       if(hash_operation[:4] !="0000"):
         return False
       previews_block= block
       block_index +=1
     return False
  def add_transaction(self,sender,receiver,amount):
    self.transactions.append({
      "sender": sender,
      "receiver": receiver,
      "amount": amount
    })
    previous_block= self.get_previous_block()
    return previous_block["index"]+1

  def add_node(self,address):
     parsed_url = urlparse(address)
     self.nodes.add(parsed_url.netloc)   
  #this method will replace my blockchain with the longest chain in world   
  def replace_chain(self):
    network= self.nodes #network all arround the world
    longest_chain = None
    max_length= len(self.chain)
    for node in network: 
      response= requests.get(f'http://{node}/get_chain')
      if(response.status_code ==200):
        length = response.json()["length"]
        chain = response.json()["chain"]
        if(length > max_length and self.is_chain_valid(chain)):
          max_length= length
          longest_chain= chain
    if(longest_chain):
        self.chain= longest_chain
        return True
    return False 


#part2 mining our blockchain

# Creating a flask server
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

#Creating an address for the node on Port 5000
node_address= str(uuid4()).replace("-","")
# Creating a Blockchain
blockchain = Blockchain()

#mining our new block
@app.route("/mine_block",methods= ["GET"])
def mine_block():
  previous_block= blockchain.get_previous_block()
  previous_proof= previous_block["proof"]
  proof= blockchain.proof_of_work(previous_proof)
  previous_hash= blockchain.hash(previous_block)
  blockchain.add_transaction(sender= node_address,receiver='Hadline',amount=1)
  block =blockchain.create_block(proof,previous_hash)
  response = {
    "message": "Congratulations, You just mined a block!",
    **block
  }
  return jsonify(response),200

@app.route("/get_chain",methods= ["GET"])
def get_chain():  
   response = {"chain": blockchain.chain,"length": len(blockchain.chain)}
   return jsonify(response),200

#checking blockchain is valid
@app.route("/is_valid",methods= ["GET"])
def is_valid():  
   is_valid = blockchain.is_chain_valid(blockchain.chain)
   if is_valid:
    response = {"message": "All good.The blockchain is valid"}
   else:
     response = {"message": "Opps! we have a problem. The blockchain is not valid"}
   return jsonify(response),200

#Adding a new transaction to the blockchain
@app.route("/add_transaction",methods= ["POST"])
def add_transaction():      
 json= request.get_json()
 transactions_keys = ['sender','receiver','amount']
 if not all (key in json for key in transactions_keys):
   return 'Some elements of the transaction are missing', 400
 index= blockchain.add_transaction(json["sender"],json["receiver"],json["amount"])  
 response= {"message": f"Transaction will be added to block {index}"}
 return jsonify(response),201
# part3 Decentralizing the blockchain 
app.run(host= "0.0.0.0",port= 5000)   

