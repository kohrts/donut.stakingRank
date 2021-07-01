import json
import requests
import csv
from datetime import date
import os


cwd = os.path.dirname(os.path.abspath(__file__))


finalData = []
compData = []
compStake = []
compAddr = []
ethtraderAddr = []

callMethod = {
    'withdraw': '0x7084f5476618d8e60b11ef0d7d3f06914655adb8793e28ff7f018d4c76d505d5', 
    'stake': '0x9e71bc8eea02a63969f509818f2dafb9254532904319f9dbda79b67bd34a5f3d', 
    'reward': '0xe2403640ba68fed3a2f88b7557551d1993f84b99bb10ff833f0cf8db0c5e0486'
    }

# api-endpoint 
# https://blockscout.com/xdai/mainnet/api-docs
stakeJSON = 'https://blockscout.com/xdai/mainnet/api?module=logs&action=getLogs&fromBlock=15881378&toBlock=latest&address=0x84b427415A23bFB57Eb94a0dB6a818EB63E2429D&topic0=0x9e71bc8eea02a63969f509818f2dafb9254532904319f9dbda79b67bd34a5f3d'
withdrawJSON = 'https://blockscout.com/xdai/mainnet/api?module=logs&action=getLogs&fromBlock=15881378&toBlock=latest&address=0x84b427415A23bFB57Eb94a0dB6a818EB63E2429D&topic0=0x7084f5476618d8e60b11ef0d7d3f06914655adb8793e28ff7f018d4c76d505d5'
usersJSON = 'https://raw.githubusercontent.com/EthTrader/donut.distribution/main/out/users_2021-06-24.json' 

# sending get request and saving the response as response object
rStakeJSON = requests.get(url = stakeJSON)
rWithdrawJSON = requests.get(url = withdrawJSON)
rUsersJSON = requests.get(url = usersJSON)

# extracting data in json format
stakeData = rStakeJSON.json()
usersData = rUsersJSON.json()


# API can return max 1000 logs
print(len(stakeData['result']))

stakeData['result'].extend(rWithdrawJSON.json()['result'])


# merge reddit usernames into json
# sort and combine data
for i, row in enumerate(stakeData['result']):
    address = '0x' + row['topics'][1][26:66].lower()   
    y = {'username': ''}
    for entry in usersData:
        if address in entry['address'].lower():
            y = {'username': entry['username']}
            
    stakeData['result'][i].update(y)
    data = int(row['data'], 16)/1e18
    
    if row['topics'][0] == callMethod['withdraw']:
        data *= -1

    if address not in compAddr:
        compAddr.append(address)

        x = {
            'username': stakeData['result'][i]['username'],
            'data': data,
            'address': address
            }

        finalData.append(x)

    else:
        dupAddrIndex = compAddr.index(address)
        finalData[dupAddrIndex]['data'] = finalData[dupAddrIndex]['data'] + data
    

# remove zero entries
length = len(finalData)-1
j = 0
while j <= length:
    if finalData[length-j]['data'] < 0.01:
        del finalData[length-j]
    j += 1


#date
today = date.today()
date = today.strftime("%Y-%m-%d")

#write files
dir = os.path.join(cwd, 'archive/donutStaking_', date)

y = json.dumps(finalData, indent = 4)
jsonFile = open(dir+'.json', 'w')
jsonFile.write(y)
jsonFile.close()


data_file = open(dir+'.csv', 'w', newline='')
csv_writer = csv.writer(data_file)
 
count = 0
for data in finalData:
    if count == 0:
        header = data.keys()
        csv_writer.writerow(header)
        count += 1
    csv_writer.writerow(data.values())
 
data_file.close()
