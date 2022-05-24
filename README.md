# Lingua-Libre-User-Audio-Downloader
A Python 3 script to download all the user files from Lingua Libre.

# Usage
To run the program, you need Python 3.6 or greater.

The program accepts two, command-line parameters and downloads the files into folder with the name of the user located in the same folder as the script.

-u or --user sets the user name.

For example, python lluad.py -u "Adélaïde Calais WMFr" will download all the files for the user Adélaïde Calais WMFr.

-a or --audio specifies the audio format, if you wish to download transcoded audio. You can choose either mp3 or ogg.

For example, python lluad.py -u "Adélaïde Calais WMFr" -a mp3 will download all the files as mp3s.

While, python lluad.py -u "Adélaïde Calais WMFr" -a ogg will download all the files as ogg files.

# Other Information
sparql.py taken from https://github.com/lingua-libre/Lingua-Libre-Bot .
