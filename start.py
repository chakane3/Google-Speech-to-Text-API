filepath = "/Users/chakaneshegog/Desktop/google_speech/"    #Input audio file path
output_filepath = "/Users/chakaneshegog/Desktop/google_speech/" #Final transcript path
bucketname = "callsaudiofiles0" #Name of the bucket created in the step before

import io
import os
from google.cloud import speech_v1p1beta1 as speech #Changed
from google.cloud.speech_v1p1beta1 import enums #Changed
from google.cloud.speech_v1p1beta1 import types #
from os.path import splitext
#from pydub import AudioSegment
import pathlib
#import google.cloud.storage as gcs
import wave
from google.cloud import storage
storage_client = storage.Client()


# convert from mp3 to wav (not really needed)
def mp3_to_wav(audio_file_name):
    if audio_file_name.split('.')[1] == 'mp3':    
        sound = AudioSegment.from_mp3(audio_file_name)
        audio_file_name = audio_file_name.split('.')[0] + '.wav'
        sound.export(audio_file_name, format="wav")

# the preferred audio format
def wav2flac(wav_path):
    flac_path = "%s.flac" % splitext(wav_path)[0]
    song = AudioSegment.from_wav(wav_path)
    song.export(flac_path, format = "flac")

def stereo_to_mono(audio_file_name):
    sound = AudioSegment.from_wav(audio_file_name)
    sound = sound.set_channels(1)
    sound.export(audio_file_name, format="wav")

def frame_rate_channel(audio_file_name):
    with wave.open(audio_file_name, "rb") as wave_file:
        frame_rate = wave_file.getframerate()
        channels = wave_file.getnchannels()
        return frame_rate,channels

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()



def google_transcribe(audio_file_name):
    
    file_name = filepath + audio_file_name
    frame_rate, channels = frame_rate_channel(file_name)
    
    if channels > 1:
        stereo_to_mono(file_name)
    
    bucket_name = bucketname
    source_file_name = filepath + audio_file_name
    destination_blob_name = audio_file_name
    
    upload_blob(bucket_name, source_file_name, destination_blob_name)
    
    gcs_uri = 'gs://' + bucketname + '/' + audio_file_name
    transcript = ''
    
    client = speech.SpeechClient()
    audio = types.RecognitionAudio(uri=gcs_uri)

    print("Setting up configurations")
    speech_context = speech.types.SpeechContext(phrases=["$OOV_CLASS_DIGIT_SEQUENCE", "$YEAR", "$PERCENT", "$MONEY", "$MONTH"])
    config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=frame_rate,
    language_code='en-US',
    enable_speaker_diarization=True,
    diarization_speaker_count=2, 
    speech_contexts = [speech_context],
    use_enhanced = True, 
    model = "phone_call") #Changed

    # Detects speech in the audio file
    print("detecting speech")
    operation = client.long_running_recognize(config, audio)
    response = operation.result(timeout=10000)
    result = response.results[-1] #Changed
    words_info = result.alternatives[0].words #Changed
    
    tag=1 #Changed
    speaker="" #Changed

    print("Assembling words")
    for word_info in words_info: #Changed
        if word_info.speaker_tag==tag: #Changed
            speaker=speaker+" "+word_info.word #Changed
        else: #Changed
            transcript += "speaker {}: {}".format(tag,speaker) + '\n' #Changed
            tag=word_info.speaker_tag #Changed
            speaker=""+word_info.word #Changed
 
    transcript += "speaker {}: {}".format(tag,speaker) #Changed
    
    delete_blob(bucket_name, destination_blob_name)
    return transcript

#google_transcribe("77.wav")





def write_transcripts(transcript_filename,transcript):
    f= open(output_filepath + transcript_filename,"w+")
    f.write(transcript)
    f.close()


if __name__ == "__main__":
    audio_file_name = "a.wav"
    print("Starting transcription")
    transcript = google_transcribe(audio_file_name)
    print("Continuing")
    transcript_filename = audio_file_name.split('.')[0] + '.txt'
    print("...")
    write_transcripts(transcript_filename,transcript)
    print("End transcription")

"""
https://www.youtube.com/watch?v=yWXzqTy9rFs 
(Netflix Will Run out of New Origional Shows in the Fall, Says Wedbush's Patcher )4 days ago

https://www.youtube.com/watch?v=HepMoaY7kS4  
(Netflix Projects Smaller than expected subscriber growth) 3 months ago 


https://www.youtube.com/watch?v=d-s50JhC4aw 4 days ago
(Netflix Q1 2020 Earnings Interview) 4 days ago

https://www.youtube.com/watch?v=zZMz9I_1vo0
(Netflix Posts Explosive Growth) 4 days ago)
"""

#how to use googles api (so far...)
#export GOOGLE_APPLICATION_CREDENTIALS="secret.json"
#pip install --upgrade google-cloud-speech
#gcloud projects add-iam-policy-binding "uhhh-274902" --member "serviceAccount:ok-121@uhhh-274902.iam.gserviceaccount.com" --role "roles/owner"
# ** make sure u have oauth, api key, and service account (set to storage admin for personal and sercie account)



"""
echo "# Google-Specch-API-Setup" >> README.md
git init
git add README.md
git commit -m "first commit"
git remote add origin https://github.com/chakane3/Google-Specch-API-Setup.git
git push -u origin master
"""