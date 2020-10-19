import requests
import json
import m3u8
import LineTVParser as PS
forceHD = True
currentPath = ''

def welcome():
    dramaID = input("Drama ID: ")
    return dramaID

def getEps(dID):
    r = requests.get("https://www.linetv.tw/api/part/"+str(dID)+"/eps/1/part")
    resJson = json.loads(r.content.decode())
    SeasonEps = resJson['dramaInfo']["eps"]
    return SeasonEps

def getInfo(ary):
    r = requests.get("https://www.linetv.tw/api/part/"+ary[0]+"/eps/"+ary[1]+"/part")
    resJson = json.loads(r.content.decode())
    if resJson["code"] != 2000:
        return [0,0,0,0,0, resJson["code"]]
    else:
        dramaName = resJson['dramaInfo']["name"]
        print('[DramaInfo:]',dramaName+' EP'+ary[1]+' '+str(resJson['dramaInfo']["year"]))
        if resJson["epsInfo"]["source"][0]["links"][0]["subtitle"] != None:
            PS.getSubtitle(resJson["epsInfo"]["source"][0]["links"][0]["subtitle"], './download/'+resJson['dramaInfo']["name"]+'_EP'+str(ary[1])+'.srt')
        m3u8Url, keyType, keyId = resJson["epsInfo"]["source"][0]["links"][0]["link"], resJson["epsInfo"]["source"][0]["links"][0]["keyType"], resJson["epsInfo"]["source"][0]["links"][0]["keyId"]
        return [ary, m3u8Url, keyType, keyId, dramaName, resJson["code"]]

if __name__ == '__main__':
    PS.init()
    dID = welcome()
    eps = getEps(dID)
    for i in range (1,eps+1):
        pramaAry = getInfo([str(dID), str(i)])
        if pramaAry[5] == 2000:
            print('[開始下載]_',i)
            PS.getFile(PS.getToken(pramaAry))
        elif pramaAry[5] == 4008:
            print("集數"+str(i)+"尚未開放!")
        elif pramaAry[5] == 4004:
            print("集數"+str(i)+"需要VIP!")