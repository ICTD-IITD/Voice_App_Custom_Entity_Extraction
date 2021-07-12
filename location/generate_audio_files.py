import os
import sys
import wave

import pandas as pd

from pydub import AudioSegment
from tqdm import tqdm

def get_clean_data(filedf):
    # Return the audio items which contains the tag 'coronavirus' & ('sos'|'impact')
    clean_df = filedf[filedf['tags'].apply(lambda x: 'coronavirus' and ('sos' or 'impact') in x)]
    return clean_df

def stereo_to_mono(audio_file_name):
    sound = AudioSegment.from_wav(audio_file_name)
    sound = sound.set_channels(1)
    sound.export(audio_file_name, format="wav")

def frame_rate_channel(audio_file_name):
    with wave.open(audio_file_name, "rb") as wave_file:
        frame_rate = wave_file.getframerate()
        channels = wave_file.getnchannels()
        return frame_rate,channels

def download_audio(audio_link, dest_pth):
    present_audios = os.listdir(dest_pth)
    # for link in audio_links: # We can loop over the audios when we want to download all audios
    aud_name = audio_link.split('/')[-1].split('.mp3')[0]
    in_file = aud_name + '.mp3'
    out_file = aud_name + '.wav'
    if out_file not in present_audios:
        try:
            os.system('wget -P ' + dest_pth + ' ' + audio_link + ' >/dev/null 2>&1') # Hides the console output, can also use subprocess
            # Convert the downloaded mp3 audio into wav format
            sound = AudioSegment.from_mp3(os.path.join(dest_pth, in_file))
            sound.export(os.path.join(dest_pth, out_file), format='wav')
            # Remove the mp3 file because we do not want its transcript
            os.system('rm ' + os.path.join(dest_pth, in_file))

            frame_rate, channels = frame_rate_channel(os.path.join(dest_pth, out_file))
            if channels > 1:
                stereo_to_mono(os.path.join(dest_pth, out_file))
            
        except Exception as e:
            print("Download error for link : {}".format(audio_link))

def download_all_audio(audio_links, dest_pth):
    for audio_link in tqdm(audio_links):
        download_audio(audio_link, dest_pth)

def main(audio_links):
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--audio_dest_pth",
        type=str,
        default="./audio_files",
    )

    args = parser.parse_args()

    download_all_audio(audio_links, args.audio_dest_pth)

if __name__ == '__main__':
    covid_filename = 'coronavirus_only_21_04_2020.xlsx'
    filedf = pd.read_excel(covid_filename)
    clean_df = get_clean_data(filedf)
    audio_links = clean_df['Recording audio link'].tolist()
    main(audio_links)
