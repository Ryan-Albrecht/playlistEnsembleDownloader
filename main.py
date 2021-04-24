from sys import argv
import requests
import re
import json
import youtube_dl

def main():
    if len(argv) != 2:
        print(f"Usage: {argv[0]} playlist_url")
        return
    playlist_url = argv[1]
    r = requests.get(playlist_url)
    print(playlist_url)
    playlist_info_json_url = re.search("playlistUrl: ?'(.*?)\?", r.text)[1]
    playlist_info = json.loads(requests.get(playlist_info_json_url).text)
    for vid in playlist_info["publishing"]:
        base_name = vid['name'].replace('/','-')
        page = requests.get(f"https://media.cedarville.edu/hapi/v1/Contents/{vid['id']}/Launch")
        m3u8_match_obj = re.search('"file":"(.+m3u8)"', page.text)
        m3u8_file_url = m3u8_match_obj[1]
        vtt_file_url = re.search('"file":"(.+vtt)"', page.text[m3u8_match_obj.end(1):])[1]
        # download video file
        # youtube-dl does not like port numbers
        m3u8_file_url = m3u8_file_url.replace(":443","")
        ydl_opts = {"outtmpl": f"{playlist_info['playlist']['name']}/{base_name}.mp4"}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([m3u8_file_url])
        # download subtitle file
        with open( f"{playlist_info['playlist']['name']}/{base_name}.vtt",'w') as f:
            f.write(requests.get(vtt_file_url).text)
        return


if __name__ == "__main__":
    main()