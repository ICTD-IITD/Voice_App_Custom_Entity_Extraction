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
        # "speech_contexts": [{ "phrases":["हाँ"]}],#"$OPERAND"] }],
        # "metadata": metadata,
    }
    audio = {"uri": storage_uri}

    operation = client.long_running_recognize(config, audio)

    # print(u"Waiting for operation to complete...")
    response = operation.result()

    transcripts = []
    print(response.results)
    for result in response.results:
        # First alternative is the most probable result
        alternative = result.alternatives[0]
        transcripts.append(alternative.transcript)

    transcript = ' '.join(transcripts)
    print("Here : {}".format(transcript))
    return transcript


# [END speech_transcribe_async_gcs]

def generate_transcripts(audio_links, transcript_dest_pth, audio_dest_pth, bucket_name, key_json):
    print('HERE')
    try:
        if not os.path.exists(transcript_dest_pth):
            os.mkdir(transcript_dest_pth)
        if not os.path.exists(audio_dest_pth):
            os.mkdir(audio_dest_pth)

        present_transcripts = os.listdir(transcript_dest_pth)
        present_audios = os.listdir(audio_dest_pth)

        transcripts = []
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_json
        for audio_link in tqdm(audio_links):
            #aud_name = audio_link.split('/')[-1].split('.mp3')[0]
            print(audio_link)
            aud_name = audio_link.split('.mp3')[0]

            trans_file = aud_name + '.txt'
            aud_file = aud_name + '.wav'

            if trans_file not in present_transcripts and aud_file in present_audios:
                try:
                    upload_blob(bucket_name, os.path.join(audio_dest_pth, aud_file), aud_file)
                    storage_uri = 'gs://' + bucket_name + '/' + aud_file

                    transcript = sample_long_running_recognize(storage_uri, key_json)
                    # print("Transcript is : {}".format(transcript))
                    delete_blob(bucket_name, aud_file)
                except Exception as e:
                    print("Error with audio : {} and error : {}".format(aud_name, str(e)))
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
        # print("Transcript : {}".format(transcripts))
    except Exception as e:
        print("Exception: {}".format(str(e)))
    return transcripts

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--key_json", type=str,
        default="mapmyindia-gv-781b65a2d6b3.json",
    )
    parser.add_argument("--transcript_dest_pth", type=str,
        default="auto_transcripts_mkbksh",
    )
    parser.add_argument("--audio_dest_pth", type=str,
        default="audio_files_mkbksh",
    )
    parser.add_argument("--bucket_name", type=str,
        default="mmitranscriptaudio",
    )

    args = parser.parse_args()

    # audio_links = ['http://voice.gramvaani.org/fsmedia/recordings/387/4086232.mp3']
    # ids = ['727754', '728692', '728996', '729714', '730350', '730872', '731180', '731332', '732569', '734713', '740592', '744277', '757951', '758308', '762311', '765912', '765928', '765986', '766000', '766031', '766096', '766135', '766175', '766193', '766197', '766277', '766283', '766292', '767927', '769264', '769346', '769720', '769771', '769949', '769968', '769973', '770027', '770103', '770105', '770109', '770115', '770127', '770156', '770190', '770228', '770229', '770231', '770406', '770687', '770778', '770781', '772309', '773989', '774432', '774888', '775108', '775122', '775427', '775563', '775594', '776053', '776055', '776079', '776191', '776268', '776275', '776350', '776443', '776592', '776818', '777260', '777461', '778251', '778265', '778269', '778297', '778366', '778387', '778438', '778603', '778751', '778934', '779176', '779261', '779614', '779630', '779920', '779951', '780557', '780727', '781010', '781062', '781185', '781234', '781267', '781332', '781476', '781789', '782136', '782198', '782283', '782384', '782395', '782408', '782410', '782440', '782447', '782470', '782634', '782641', '782654', '782794', '782795', '782871', '782919', '782945', '783202', '783337', '783342', '783428', '783439', '787619', '787632', '787650', '787666', '787821', '787856', '787890', '787907', '788088', '788773', '788813']
    # audio_links = ['http://voice2.gramvaani.org/fsmedia/recordings/922/1264807.mp3', 'http://voice2.gramvaani.org/fsmedia/recordings/922/1266673.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1267839.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1269371.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1271277.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1272294.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1273116.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1273547.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1276142.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1280773.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1293909.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1300555.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1328683.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1329413.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1340108.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1349459.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1349480.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1349559.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1349580.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1349617.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1349696.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1349736.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1349776.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1349795.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1349799.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1349879.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1349885.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1349894.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1352644.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1355452.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1355549.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1356837.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1356956.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1357475.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1357509.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1357518.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1357731.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1357895.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1357900.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1357920.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1357931.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1357951.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1358056.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1358176.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1358239.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1358240.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1358242.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1358625.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1359434.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1359580.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1359583.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1366766.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1372508.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1373964.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1375587.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1376087.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1376142.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1376855.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1377159.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1377237.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1378997.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1379000.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1379085.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1379452.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1379576.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1379583.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1379809.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1380030.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1380491.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1381273.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1382436.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1383159.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1385788.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1385824.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1385845.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1385936.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1386184.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1386222.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1386387.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1386998.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1387364.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1387934.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1389374.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1389837.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1391333.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1391413.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1392273.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1392364.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1393811.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1394191.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1394914.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1394996.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1395302.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1395400.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1395568.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1395822.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1396076.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1396842.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1397729.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1397959.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1398201.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1398486.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1398506.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1398522.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1398524.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1398595.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1398604.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1398672.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1399163.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1399220.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1399234.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1399549.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1399550.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1399824.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1399914.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1400002.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1400731.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1401030.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1401035.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1401279.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1401290.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1417410.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1417483.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1417524.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1417544.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1417768.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1417839.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1417883.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1417902.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1418186.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1420126.mp3' , 'http://voice2.gramvaani.org/fsmedia/recordings/922/1420344.mp3']

    # audio_links = ['http://voice.gramvaani.org/fsmedia/recordings/977/3821018.mp3']
    # audio_links = ['http://voice.gramvaani.org/fsmedia/recordings/1129/3944676.mp3']
    # audio_links = ['http://voice.gramvaani.org/fsmedia/recordings/1129/3706424.mp3']
    # audio_links = ['http://voice.gramvaani.org/fsmedia/recordings/1129/2744876.mp3']
    # audio_links = ['4570980.mp3','4570993.mp3']
    audio_links = ['http://voice.gramvaani.org/fsmedia/recordings/1129/4034394.mp3', 'http://voice.gramvaani.org/fsmedia/recordings/1129/4111538.mp3']
    transcripts = generate_transcripts(audio_links, args.transcript_dest_pth,\
        args.audio_dest_pth, args.bucket_name, args.key_json)

    # sys.exit()
    out_df = pd.DataFrame({'Audio Link': audio_links, 'ML Transcript':transcripts})
    out_df.to_excel('jeevika_ml_transcripts.xlsx', index=False)

if __name__ == "__main__":
    main()


# नमस्कार आपने गाजीपुर मोबाइल वाणी मैं हूं समझ आता उपेंद्र कुमार लोगों को पता चला है कि गाजीपुर से बाहर है जखनिया और दुल्लापुर की दुकानों सहित आसपास के सभी क्षेत्रों में लोग धड़ाधड़ चालू कर दुकान चालू कर दी है बाजारों में चारों तरफ भीड़ नजर आई और फिर करुणा का खाओ आम आदमी की थाली पहुंचा इस कारण रोजमर्रा में प्रयोग होने वाली वस्तुओं में बीते दिनों की तुलना में सब्जियों के भाव में काफी उछाल आ गए आलू प्याज टमाटर गोभी भिंडी और बैगन के रेट में अचानक उछाल आ गया इसकी प्रमुख वजह को लेकर एक साथ एक-दो दिन नहीं बल्कि सप्ताह भर के लिए सब्जी तक भी स्टोर कर रहे हैं लोग वहीं व्यापारी ज्यादा मुनाफा कमाने के चक्कर में सब्जियों को ब्लैक मार्केटिंग भी कर रहे हैं साथ ही इस भयावह स्थिति से निपटने का तरीका ही पक्ष
# नमस्कार आपने गाजीपुर मोबाइल वाणी मैं हूं समझ आता उपेंद्र कुमार लोगों को पता चला है कि गाजीपुर से बाहर है जखनिया और दुल्लापुर की दुकानों सहित आसपास के सभी क्षेत्रों में लोग धड़ाधड़ चालू कर दुकान चालू कर दी है बाजारों में चारों तरफ भीड़ नजर आई और फिर करुणा का खाओ आम आदमी की थाली पहुंचा इस कारण रोजमर्रा में प्रयोग होने वाली वस्तुओं में बीते दिनों की तुलना में सब्जियों के भाव में काफी उछाल आ गए आलू प्याज टमाटर गोभी भिंडी और बैगन के रेट में अचानक उछाल आ गया इसकी प्रमुख वजह को लेकर एक साथ एक-दो दिन नहीं बल्कि सप्ताह भर के लिए सब्जी तक भी स्टोर कर रहे हैं लोग वहीं व्यापारी ज्यादा मुनाफा कमाने के चक्कर में सब्जियों को ब्लैक मार्केटिंग भी कर रहे हैं साथ ही इस भयावह स्थिति से निपटने का तरीका ही पक्ष
# Ground Truth:
# नमस्कार आप सुन रहे हैं गाज़ीपुर मोबाइल वाणी में हूँ संवाददाता उपेंद्र कुमार आज जैसे ही लोगों को पता चला है कि ग़ाज़ीपुर लोखड़ौन से बहार है जखनिया और दुल्लापुर कि दुकानों सहित आस पास सभी क्षेत्रों में लोग धड़ाधड़ दुकान चालू कर दिए| बाज़ारों में चारो तरफ भीड़ नज़र आयी और फिर कोरोना का खौफ आम आदमी कि थाली तक जा पोहोंचा| इस कारण रोजमर्या में प्रयोग होने वाली वस्तुओं में बीते दिनों कि तुलना में सब्जियों के भाव में काफी उछाल आ गया आलू, प्याज टमाटर, गोबी भिंडी और बैंगन के रेट में अचानक उछाल आ गया गया इसकी प्रमुख वजा कोरोना को लेकर कोरोना को लेकर एक साथ एक दो दिन नहीं बल्कि सप्ताह भर के लिए सब्जी तक के लिए भी स्टोर कर रहे हैं लोग वही व्यापारी ज़ादा मुनाफा कमाने के चक्कर में सब्जियों को ब्लैक मार्केटिंग भी कर रहे हैं साथ ही इस भयावह स्थिति से निपटने का तरीका ही बचाव है तो लोगों ने अपना दिमाग लगाना शुरू कर दिया हैं की न जाने हमारा जिल्ला ग़ाज़ीपुर भी लोखड़ौन के स्थिति में शामिल हो जाये इसलिए लोग आज से ही ज़रुरत की सभी सामने को स्टोर करना शुरू कर दिए हैं लगबघ यह ही स्थिति हॉस्टपिकल बाजार किराना स्टोर जनरल स्टोर सभी दुकानदारों की आज जैसे ही आज मार्किट खुला और बिक्री धड़ाधड़ चली
