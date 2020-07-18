import os
import shutil
from tqdm import tqdm
import zipfile
import json
import requests
import vtt2srt as V2S
forceHD = True
currentPath = ''
def init():
	global currentPath
	currentPath = os.getcwd().replace('\\','/')
	if not os.path.isdir('./bin'):
		os.mkdir('./bin')
	if not os.path.isdir('./download'):
		os.mkdir('./download')
	if not os.path.isfile('./bin/youtube-dl.exe'):
		print('[SysInfo:]youtube-dl not found!\nDownloading...')
		dlFile('https://yt-dl.org/downloads/latest/youtube-dl.exe', './bin/youtube-dl.exe')
	if not os.path.isfile('./bin/ffmpeg.exe'):
		print('[SysInfo:]ffmpeg not found!\nDownloading...')
		dlFile('https://ffmpeg.zeranoe.com/builds/win32/static/ffmpeg-latest-win32-static.zip', './bin/ffmpeg-latest-win32-static.zip')
		print('Unziping...')
		with zipfile.ZipFile('./bin/ffmpeg-latest-win32-static.zip', 'r') as zip_ref:
			zip_ref.extractall('./bin')
		os.remove('./bin/ffmpeg-latest-win32-static.zip')
		shutil.move('./bin/ffmpeg-latest-win32-static/bin/ffmpeg.exe', "./bin/ffmpeg.exe")
		shutil.rmtree('./bin/ffmpeg-latest-win32-static')

def dlFile(url, path):
	r = requests.get(url, stream=True)
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

def welcome():
	VideoLink = input("Video Link: ")
	episode, dramaID = VideoLink.split('/')[-1], VideoLink.split('/')[-3]
	return [dramaID, episode]

def getInfo(ary):
	r = requests.get("https://www.linetv.tw/api/part/"+ary[0]+"/eps/"+ary[1]+"/part")
	resJson = json.loads(r.content.decode())
	dramaName = resJson['dramaInfo']["name"]
	print('[DramaInfo:]',dramaName+' EP'+ary[1]+' '+str(resJson['dramaInfo']["year"]))
	if resJson["epsInfo"]["source"][0]["links"][0]["subtitle"] != None:
		getSubtitle(resJson["epsInfo"]["source"][0]["links"][0]["subtitle"], './download/'+resJson['dramaInfo']["name"]+'_EP'+str(resJson['dramaInfo']["eps"])+'.srt')
	m3u8Url, keyType, keyId = resJson["epsInfo"]["source"][0]["links"][0]["link"], resJson["epsInfo"]["source"][0]["links"][0]["keyType"], resJson["epsInfo"]["source"][0]["links"][0]["keyId"]
	return [ary, m3u8Url, keyType, keyId, dramaName]

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
	V2S.vtt_to_srt(path)

def getToken(ary):
	queryjson = {
	'keyType':ary[2],
	'keyId':ary[3],
	'dramaId':ary[0][0],
	'eps':ary[0][1] 
	}
	r = requests.post("https://www.linetv.tw/api/part/dinosaurKeeper", json = queryjson)
	resJson = json.loads(r.content.decode())
	return [ary, 'authentication:' + resJson['token']]

def getFile(ary):
	global currentPath
	if forceHD:
		url = ary[0][1].replace('SD','HD')
	else:
		url = ary[0][1]
	os.system(currentPath + '/bin/youtube-dl.exe --add-header ' + '"' + str(ary[1]) + '" ' + url +' --output ./download/"' + str(ary[0][4]+'_EP'+ary[0][0][1]) + '.mp4"')

init()
getFile(getToken((getInfo(welcome()))))