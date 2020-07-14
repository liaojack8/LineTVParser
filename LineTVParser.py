import os
from tqdm import tqdm
import json
import requests
forceHD = True

def init():
	if not os.path.isdir('./bin'):
		os.mkdir('./bin')
	if not os.path.isdir('./download'):
		os.mkdir('./download')
	if not os.path.isfile('./bin/youtube-dl.exe'):
		print('youtube-dl not found!\nDownloading...')
		r = requests.get('https://yt-dl.org/downloads/latest/youtube-dl.exe', stream=True)
		is_chunked = r.headers.get('transfer-encoding', '') == 'chunked'
		content_length_s = r.headers.get('content-length')
		if not is_chunked and content_length_s.isdigit():
			content_length = int(content_length_s)
		else:
			content_length = None
		pbar = tqdm(total=content_length, unit="B", unit_scale=True, ncols=100)
		with open('./bin/youtube-dl.exe', 'wb') as f:
			for chunk in r.iter_content(chunk_size=1024 * 1024):
				f.write(chunk)
				pbar.update(len(chunk))
			pbar.close()
		f.close()

def welcome():
	VideoLink = 'https://www.linetv.tw/drama/10900/eps/1'#input("Video Link: ")
	return [VideoLink.split('/')[-1], VideoLink.split('/')[-3]] #episode, dramaID

def getInfo(ary):
	r = requests.get("https://www.linetv.tw/api/part/"+ary[1]+"/eps/"+ary[0]+"/part")
	resJson = json.loads(r.content.decode())
	print('[DramaInfo:]',resJson['dramaInfo']["name"]+' EP'+str(resJson['dramaInfo']["eps"])+' '+str(resJson['dramaInfo']["year"]))
	if resJson["epsInfo"]["source"][0]["links"][0]["subtitle"] != None:
		getSubtitle(resJson["epsInfo"]["source"][0]["links"][0]["subtitle"], './download/'+resJson['dramaInfo']["name"]+'_EP'+str(resJson['dramaInfo']["eps"])+'.srt')
	#m3u8Url, keyType, keyId, dramaID
	return [ary, resJson["epsInfo"]["source"][0]["links"][0]["link"], resJson["epsInfo"]["source"][0]["links"][0]["keyType"], resJson["epsInfo"]["source"][0]["links"][0]["keyId"]]

def getSubtitle(subtitleLink, path):
	r = requests.get(subtitleLink, stream=True)
	is_chunked = r.headers.get('transfer-encoding', '') == 'chunked'
	content_length_s = r.headers.get('content-length')
	if not is_chunked and content_length_s.isdigit():
		content_length = int(content_length_s)
	else:
		content_length = None
	pbar = tqdm(total=content_length, unit="B", unit_scale=True, ncols=100)
	with open(path, 'wb') as f:
		for chunk in r.iter_content(chunk_size=1024 * 1024):
			f.write(chunk)
			pbar.update(len(chunk))
		pbar.close()
	f.close()

def getToken(ary):
	queryjson = {
	'keyType':ary[2],
	'keyId':ary[3],
	'dramaId':ary[0][1],
	'eps':ary[0][0]
	}
	r = requests.post("https://www.linetv.tw/api/part/dinosaurKeeper", json = queryjson)
	resJson = json.loads(r.content.decode())
	if forceHD:
		return [ary[1].replace('SD','HD'), 'authentication:' + resJson['token']]
	else:
		return [ary[1], 'authentication:' + resJson['token']]


# init()
print(getToken((getInfo(welcome()))))
