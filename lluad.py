# Copyright 2022 Rodion Kosovsky; License: GPL 3
import os
import re
import requests
import sparql
import argparse


global download_path, audio_extension

ENDPOINT = "https://lingualibre.org/bigdata/namespace/wdq/sparql"
API = "https://lingualibre.org/api.php"
BASEQUERY = """
SELECT DISTINCT
    ?record ?file
WHERE {
  ?record prop:P2 entity:Q2 .
  ?record prop:P3 ?file .
  ?record prop:P5 ?speaker .
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en" .
  }
  #filters
}"""


def download_audio(filename):

    # In the url replace ? with %3F as Commons does.
    url = f"https://commons.wikimedia.org/wiki/File:{filename.replace('?', '%3F')}"

    # Commons requires a valid User-Agent or it returns a 403 error.
    headers = {'User-Agent': 'LibreLingua User File Downloader Alpha'}

    # Download the HTML for the file
    content = requests.get(url, headers=headers).text

    '''
    Find the download link to the file in the HTML using a regex.
    If the file is not transcoded, then it has the same location in the html. 
    Otherwise, the specific transcoding requires finding.
    '''
    if audio_extension == "mp3" and filename.endswith("wav"):
        mp3_url = re.search(
                        r'<source src="(https://upload.wikimedia.org/[\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])" '
                        r'type="audio/mpeg" data-title="MP3" data-shorttitle="MP3" data-transcodekey="mp3"'
                        r' data-width="0" data-height="0" data-bandwidth="\d*"/>', content)
        if mp3_url:
            download_url = mp3_url.groups()[0]
            download_filename = f"{filename.replace('?','')}.mp3"
        else:
            print(f"No mp3 file found for {filename}")
            return False
    elif audio_extension == "ogg" and filename.endswith("wav"):
        ogg_url = re.search(
                        r'<source src="(https://upload.wikimedia.org/[\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])" '
                        r'type="audio/ogg; codecs=&quot;vorbis&quot;" data-title="Ogg Vorbis" '
                        r'data-shorttitle="Ogg Vorbis" data-transcodekey="ogg" data-width="0" '
                        r'data-height="0" data-bandwidth="\d*"/>', content)
        if ogg_url:
            download_url = ogg_url.groups()[0]
            download_filename = f"{filename.replace('?','')}.ogg"
        else:
            print(f"No mp3 file found for {filename}")
            return False
    else:
        common_url = re.search(
            r'<div class="fullMedia"><p><a href="(https://upload.wikimedia.org/[\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"',
            content)
        if common_url:
            download_url = common_url.groups()[0]
            download_filename = f"{filename.replace('?', '')}"
        else:
            print(f"No download link found for found for {filename}")
            return False

    # Common files are generally safe for downloading, but ? need to be removed
    common_file = requests.get(download_url, headers=headers)

    save_name = os.path.join(download_path, download_filename)
    try:
        with open(save_name, 'wb') as audio_file:
            audio_file.write(common_file.content)
    except OSError:
        return False

    return True


def get_records(user_name):
    # Set the Sparql query to only return results for the requested user.
    filters = f'?speaker prop:P11 ?linkeduser. FILTER( ?linkeduser = "{user_name}" ).'
    print(f"Getting records for {user_name} records.")

    # Run the Sparql query.
    raw_records = sparql.request(ENDPOINT, BASEQUERY.replace("#filters", filters))
    print(f"Found {len(raw_records)} records.")

    for record in raw_records:
        file = sparql.format_value(record, "file")
        print(f"Downloading: {file}")
        download_audio(file)


def create_folder(path):
    try:
        if os.path.isdir(path):
            pass
        else:
            os.makedirs(path)
    except IOError as exception:
        raise IOError('%s: %s' % (path, exception.strerror))
    return None


parser = argparse.ArgumentParser(description='Download the audio files recorded by a user.')
parser.add_argument('-u', '--user', type=str,
                    help='The name of the user that recorded the files')
parser.add_argument('-a', '--audio', type=str,
                    help='The format of the audio files that you wish to download. Can be "mp3", "ogg", or "wav".'
                         'The default is "wav".')



args = parser.parse_args()
# Paste the username into the ""
user = args.user

# This controls whether to return a transcoded audio file. It can be either "mp3" "ogg" or "".
audio_extension = args.audio

# Either create a folder named after the user or use an existing one.
create_folder(user)

# Set the download path for the files.
download_path = os.path.join(os.path.dirname(__file__), f"{args.user}")

# Not that everything is set up, fetch all the user files.
get_records(user)
