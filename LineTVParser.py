import os
import m3u8
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
		#dlFile('https://ffmpeg.zeranoe.com/builds/win32/static/ffmpeg-latest-win32-static.zip', './bin/ffmpeg-latest-win32-static.zip')
		r = requests.get('https://api.github.com/repos/marierose147/ffmpeg_windows_exe_with_fdk_aac/releases/latest')
		dlFile(json.loads(r.content.decode())['assets'][2]['browser_download_url'], './bin/ffmpeg.exe')
		# print('Unziping...')
		# with zipfile.ZipFile('./bin/ffmpeg-latest-win32-static.zip', 'r') as zip_ref:
		# 	zip_ref.extractall('./bin')
		# os.remove('./bin/ffmpeg-latest-win32-static.zip')
		# shutil.move('./bin/ffmpeg-latest-win32-static/bin/ffmpeg.exe', "./bin/ffmpeg.exe")
		# shutil.rmtree('./bin/ffmpeg-latest-win32-static')

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
		getSubtitle(resJson["epsInfo"]["source"][0]["links"][0]["subtitle"], './download/'+resJson['dramaInfo']["name"]+'_EP'+str(ary[1])+'.srt')
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

def urlParser(uu,flag=False): # flag = force 1080p
    variant_m3u8 = m3u8.load(uu)
    # print('Supported resolution of this video:',end='\n')
    # for i in range(len(variant_m3u8.playlists)):
    #     print(variant_m3u8.playlists[i].uri.split('/')[0], end='\t')
    #     print(uu.split('v1')[0]+'v1/'+variant_m3u8.playlists[i].uri)
    Vnum = uu.split('/')[5]
    if flag:# force 1080p video
        if len(uu.split('/')) == 7:
            return (uu.split(Vnum)[0]+Vnum+'/'+variant_m3u8.playlists[len(variant_m3u8.playlists)-1].uri).replace(variant_m3u8.playlists[len(variant_m3u8.playlists)-1].uri.split('/')[0],'1080').replace(variant_m3u8.playlists[len(variant_m3u8.playlists)-1].uri.split('/')[0]+'p','1080p')
    else:# HD
        if len(uu.split('/')) == 7:
            return uu.split(Vnum)[0]+Vnum+'/'+variant_m3u8.playlists[len(variant_m3u8.playlists)-1].uri

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
	url = urlParser(url,False)
	os.system(currentPath + '/bin/youtube-dl.exe --add-header ' + '"' + str(ary[1]) + '" ' + url +' --output ./download/"' + str(ary[0][4]+'_EP'+ary[0][0][1]) + '.mp4"')

if __name__ == '__main__':
	init()
	getFile(getToken((getInfo(welcome()))))