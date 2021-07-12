import os
import sys

import pandas as pd

from generate_audio_files import download_audio
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
from google.cloud import storage
from tqdm import tqdm

def get_clean_data(filedf):
    # Return the audio items which contains the tag 'coronavirus' & ('sos'|'impact')
    clean_df = filedf[filedf['tags'].apply(lambda x: 'coronavirus' and ('sos' or 'impact') in x)]
    return clean_df

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.delete()

def sample_long_running_recognize(storage_uri, key_json):
    """
    Transcribe long audio file from Cloud Storage using asynchronous speech
    recognition
    https://github.com/googleapis/python-speech/blob/master/samples/v1/speech_transcribe_async_gcs.py

    Args:
      storage_uri URI for audio file in Cloud Storage, e.g. gs://[BUCKET]/[FILE]
    """

    client = speech_v1.SpeechClient()

    # storage_uri = 'gs://cloud-samples-data/speech/brooklyn_bridge.raw'

    # Sample rate in Hertz of the audio data sent
    # sample_rate_hertz = 16000

    # The language of the supplied audio
    language_code = "hi-IN"

    # Encoding of audio data sent. This sample sets this explicitly.
    # This field is optional for FLAC and WAV audio formats.
    encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16
    # interaction_type = enums.RecognitionMetadata.InteractionType.VOICE_SEARCH
    recording_device_type = enums.RecognitionMetadata.RecordingDeviceType.SMARTPHONE
    metadata = {
        "interaction_type": enums.RecognitionMetadata.InteractionType.VOICEMAIL,
        "original_media_type": enums.RecognitionMetadata.OriginalMediaType.AUDIO,
        "recording_device_type": enums.RecognitionMetadata.RecordingDeviceType.PHONE_LINE,
        "original_mime_type": "audio/mp3",
    }
    config = {
        # "sample_rate_hertz": sample_rate_hertz,
        "language_code": language_code,
        "encoding": encoding,
        # "metadata": metadata,
    }
    audio = {"uri": storage_uri}

    operation = client.long_running_recognize(config, audio)

    # print(u"Waiting for operation to complete...")
    response = operation.result()

    transcripts = []
    for result in response.results:
        # First alternative is the most probable result
        alternative = result.alternatives[0]
        transcripts.append(alternative.transcript)

    transcript = ' '.join(transcripts)
    return transcript


# [END speech_transcribe_async_gcs]

def generate_transcripts(audio_links, transcript_dest_pth, audio_dest_pth, bucket_name, key_json, manual_transcripts, generate_speech2text):
    if not os.path.exists(transcript_dest_pth):
        os.mkdir(transcript_dest_pth)
    if not os.path.exists(audio_dest_pth):
        os.mkdir(audio_dest_pth)

    present_transcripts = os.listdir(transcript_dest_pth)
    present_audios = os.listdir(audio_dest_pth)

    transcripts = []

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_json
    for audio_link, manual_transcript, generate_flag in tqdm(zip(audio_links, manual_transcripts, generate_speech2text), total=len(audio_links)):
        aud_name = audio_link.split('/')[-1].split('.mp3')[0]

        trans_file = aud_name + '.txt'
        aud_file = aud_name + '.wav'

        if trans_file not in present_transcripts and aud_file in present_audios and generate_flag == 1:
            try:
                upload_blob(bucket_name, os.path.join(audio_dest_pth, aud_file), aud_file)
                storage_uri = 'gs://' + bucket_name + '/' + aud_file

                transcript = sample_long_running_recognize(storage_uri, key_json)
                # print("Transcript is : {}".format(transcript))
                delete_blob(bucket_name, aud_file)
            except Exception as e:
                print("Error with audio : {}".format(aud_name))
                with open('errors.txt', 'a') as f:
                    f.write(aud_name + '\n')
                transcript = ''

            with open(os.path.join(transcript_dest_pth, trans_file), 'w') as f:
                f.write(transcript)
            transcripts.append(transcript)
        else:
            try:
                with open(os.path.join(transcript_dest_pth, trans_file), 'r') as f:
                    transcript = f.read()
                    transcript = transcript.strip()
            except:
                transcript = ''
            transcripts.append(transcript)
    return transcripts

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--covid_filename", type=str,
        default='coronavirus_and_sos_1.xlsx',
    )
    parser.add_argument("--key_json", type=str,
        default="mapmyindia-gv-781b65a2d6b3.json",
    )
    parser.add_argument("--transcript_dest_pth", type=str,
        default="auto_transcripts",
    )
    parser.add_argument("--audio_dest_pth", type=str,
        default="audio_files",
    )
    parser.add_argument("--bucket_name", type=str,
        default="mmitranscriptaudio",
    )
    parser.add_argument("--manual_transcript_bool", type=bool,
        default=False,
    )

    args = parser.parse_args()

    covid_filename = args.covid_filename
    filedf = pd.read_excel(covid_filename)
    clean_df = get_clean_data(filedf)
    audio_links = clean_df['Recording audio link'].tolist()
    manual_transcripts = clean_df['transcription'].tolist()

    transcripts = generate_transcripts(audio_links, args.transcript_dest_pth,\
        args.audio_dest_pth, args.bucket_name, args.key_json, manual_transcripts)

    clean_df['automatic_transcripts'] = transcripts
    clean_df.to_csv('auto_transcripts.csv', index=False)


if __name__ == "__main__":
    main()


# नमस्कार आपने गाजीपुर मोबाइल वाणी मैं हूं समझ आता उपेंद्र कुमार लोगों को पता चला है कि गाजीपुर से बाहर है जखनिया और दुल्लापुर की दुकानों सहित आसपास के सभी क्षेत्रों में लोग धड़ाधड़ चालू कर दुकान चालू कर दी है बाजारों में चारों तरफ भीड़ नजर आई और फिर करुणा का खाओ आम आदमी की थाली पहुंचा इस कारण रोजमर्रा में प्रयोग होने वाली वस्तुओं में बीते दिनों की तुलना में सब्जियों के भाव में काफी उछाल आ गए आलू प्याज टमाटर गोभी भिंडी और बैगन के रेट में अचानक उछाल आ गया इसकी प्रमुख वजह को लेकर एक साथ एक-दो दिन नहीं बल्कि सप्ताह भर के लिए सब्जी तक भी स्टोर कर रहे हैं लोग वहीं व्यापारी ज्यादा मुनाफा कमाने के चक्कर में सब्जियों को ब्लैक मार्केटिंग भी कर रहे हैं साथ ही इस भयावह स्थिति से निपटने का तरीका ही पक्ष
# नमस्कार आपने गाजीपुर मोबाइल वाणी मैं हूं समझ आता उपेंद्र कुमार लोगों को पता चला है कि गाजीपुर से बाहर है जखनिया और दुल्लापुर की दुकानों सहित आसपास के सभी क्षेत्रों में लोग धड़ाधड़ चालू कर दुकान चालू कर दी है बाजारों में चारों तरफ भीड़ नजर आई और फिर करुणा का खाओ आम आदमी की थाली पहुंचा इस कारण रोजमर्रा में प्रयोग होने वाली वस्तुओं में बीते दिनों की तुलना में सब्जियों के भाव में काफी उछाल आ गए आलू प्याज टमाटर गोभी भिंडी और बैगन के रेट में अचानक उछाल आ गया इसकी प्रमुख वजह को लेकर एक साथ एक-दो दिन नहीं बल्कि सप्ताह भर के लिए सब्जी तक भी स्टोर कर रहे हैं लोग वहीं व्यापारी ज्यादा मुनाफा कमाने के चक्कर में सब्जियों को ब्लैक मार्केटिंग भी कर रहे हैं साथ ही इस भयावह स्थिति से निपटने का तरीका ही पक्ष
# Ground Truth:
# नमस्कार आप सुन रहे हैं गाज़ीपुर मोबाइल वाणी में हूँ संवाददाता उपेंद्र कुमार आज जैसे ही लोगों को पता चला है कि ग़ाज़ीपुर लोखड़ौन से बहार है जखनिया और दुल्लापुर कि दुकानों सहित आस पास सभी क्षेत्रों में लोग धड़ाधड़ दुकान चालू कर दिए| बाज़ारों में चारो तरफ भीड़ नज़र आयी और फिर कोरोना का खौफ आम आदमी कि थाली तक जा पोहोंचा| इस कारण रोजमर्या में प्रयोग होने वाली वस्तुओं में बीते दिनों कि तुलना में सब्जियों के भाव में काफी उछाल आ गया आलू, प्याज टमाटर, गोबी भिंडी और बैंगन के रेट में अचानक उछाल आ गया गया इसकी प्रमुख वजा कोरोना को लेकर कोरोना को लेकर एक साथ एक दो दिन नहीं बल्कि सप्ताह भर के लिए सब्जी तक के लिए भी स्टोर कर रहे हैं लोग वही व्यापारी ज़ादा मुनाफा कमाने के चक्कर में सब्जियों को ब्लैक मार्केटिंग भी कर रहे हैं साथ ही इस भयावह स्थिति से निपटने का तरीका ही बचाव है तो लोगों ने अपना दिमाग लगाना शुरू कर दिया हैं की न जाने हमारा जिल्ला ग़ाज़ीपुर भी लोखड़ौन के स्थिति में शामिल हो जाये इसलिए लोग आज से ही ज़रुरत की सभी सामने को स्टोर करना शुरू कर दिए हैं लगबघ यह ही स्थिति हॉस्टपिकल बाजार किराना स्टोर जनरल स्टोर सभी दुकानदारों की आज जैसे ही आज मार्किट खुला और बिक्री धड़ाधड़ चली
