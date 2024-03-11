from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
import datetime
import ipfsapi
import os
import json
from web3 import Web3, HTTPProvider
from django.core.files.storage import FileSystemStorage
import pickle

api = ipfsapi.Client(host='http://127.0.0.1', port=5001)
global details, username

def readDetails(contract_type):
    global details
    details = ""
    print(contract_type+"======================")
    blockchain_address = 'http://127.0.0.1:9545' #Blokchain connection IP
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'BlockchainOSN.json' #Blockchain OSN contract code
    deployed_contract_address = '0x3bE83466Bb7159c97a01e84c977F37397b9BddE7' #hash address to access OSN contract
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi) #now calling contract to access data
    if contract_type == 'signup':
        details = contract.functions.getSignup().call()
    if contract_type == 'tweets':
        details = contract.functions.getPublishTweets().call()    
    print(details)    

def saveDataBlockChain(currentData, contract_type):
    global details
    global contract
    details = ""
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'BlockchainOSN.json' #Blockchain contract file
    deployed_contract_address = '0x3bE83466Bb7159c97a01e84c977F37397b9BddE7' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    readDetails(contract_type)
    if contract_type == 'signup':
        details+=currentData
        msg = contract.functions.setSignup(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'tweets':
        details+=currentData
        msg = contract.functions.setPublishTweets(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})

def Signup(request):
    if request.method == 'GET':
       return render(request, 'Signup.html', {})

def PublishTweets(request):
    if request.method == 'GET':
       return render(request, 'PublishTweets.html', {})

def ViewTweets(request):
    #data = "post#"+user+"#"+post_message+"#"+str(hashcode)+"#"+str(current_time)
    if request.method == 'GET':
        strdata = '<table border=1 align=center width=100%><tr><th><font size="" color="black">Tweet Owner</th><th><font size="" color="black">Tweet Message</th>'
        strdata+='<th><font size="" color="black">IPFS Image Hashcode</th><th><font size="" color="black">Tweet Image</th>'
        strdata+='<th><font size="" color="black">Tweet Date Time</th></tr>'
        for root, dirs, directory in os.walk('static/tweetimages'):
            for j in range(len(directory)):
                os.remove('static/tweetimages/'+directory[j])
        readDetails('tweets')
        arr = details.split("\n")
        for i in range(len(arr)-1):
            array = arr[i].split("#")
            if array[0] == 'post':
                content = api.get_pyobj(array[3])
                content = pickle.loads(content)
                with open("SocialMediaApp/static/tweetimages/"+array[5], "wb") as file:
                    file.write(content)
                file.close()
                strdata+='<tr><td><font size="" color="black">'+str(array[1])+'</td><td><font size="" color="black">'+array[2]+'</td><td><font size="" color="black">'+str(array[3])+'</td>'
                strdata+='<td><img src=static/tweetimages/'+array[5]+'  width=200 height=200></img></td>'
                strdata+='<td><font size="" color="black">'+str(array[4])+'</td>'
        context= {'data':strdata}
        return render(request, 'ViewTweets.html', context)        
         

def LoginAction(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        readDetails('signup')
        arr = details.split("\n")
        status = "none"
        for i in range(len(arr)-1):
            array = arr[i].split("#")
            if array[1] == username and password == array[2]:
                status = "Welcome "+username
                break
        if status != 'none':
            file = open('session.txt','w')
            file.write(username)
            file.close()   
            context= {'data':status}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'login failed'}
            return render(request, 'Login.html', context)

        
def PublishTweetsAction(request):
    if request.method == 'POST':
        post_message = request.POST.get('t1', False)
        filename = request.FILES['t2'].name
        myfile = request.FILES['t2'].read()
        myfile = pickle.dumps(myfile)
        now = datetime.datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        user = ''
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        file.close()
        hashcode = api.add_pyobj(myfile)
        data = "post#"+user+"#"+post_message+"#"+str(hashcode)+"#"+str(current_time)+"#"+filename+"\n"
        saveDataBlockChain(data,"tweets")
        output = 'DTweet saved in Blockchain with below hashcodes & Media file saved in IPFS.<br/>'+str(hashcode)
        context= {'data':output}
        return render(request, 'PublishTweets.html', context)
        

def SignupAction(request):
    if request.method == 'POST':
        global details
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        gender = request.POST.get('t4', False)
        email = request.POST.get('t5', False)
        address = request.POST.get('t6', False)
        output = "Username already exists"
        readDetails('signup')
        arr = details.split("\n")
        status = "none"
        for i in range(len(arr)-1):
            array = arr[i].split("#")
            if array[1] == username:
                status = username+" already exists"
                break
        if status == "none":
            details = ""
            data = "signup#"+username+"#"+password+"#"+contact+"#"+gender+"#"+email+"#"+address+"\n"
            saveDataBlockChain(data,"signup")
            context = {"data":"Signup process completed and record saved in Blockchain"}
            return render(request, 'Signup.html', context)
        else:
            context = {"data":status}
            return render(request, 'Signup.html', context)




