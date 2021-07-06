package com.example.voicesurvey;


import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;

import android.Manifest;
import android.content.ActivityNotFoundException;
import android.content.ContentResolver;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.media.MediaRecorder;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.speech.RecognizerIntent;
import android.speech.tts.TextToSpeech;
import android.text.Html;
import android.util.Log;
import android.view.View;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;
import org.json.JSONObject;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.nio.charset.Charset;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.ResourceBundle;
import java.util.concurrent.TimeUnit;
import org.apache.commons.io.FileUtils;
import org.apache.commons.text.StringEscapeUtils;
import org.json.JSONException;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;


class rex
{   static String y;
    public void setstring(String s)
    {
        this.y=s;
    }
}

class final_ques_idx
{   static int ques_idx;
    public void setindex(int idx)
    {
        this.ques_idx=idx;
    }
}

@RequiresApi(api = Build.VERSION_CODES.O)

public class startSurvey extends AppCompatActivity {
    private static final int REQ_CODE_SPEECH_INPUT = 100;
    private static final String LOG_TAG = "AUDIO_RECORDER";
    private ImageButton btnSpeak;
    private TextView txtSpeechInput;
    private TextView outputText;
    private TextToSpeech textToSpeech;
    private String indexUrl;
    rex a =new rex();
    private String f_ques_idx;
    DateTimeFormatter dtf = DateTimeFormatter.ofPattern("yyyy-MM-dd_HH-mm-s");
    LocalDateTime now = LocalDateTime.now();
    String fileName = "survey "+dtf.format(now)+ ".txt";
    File file = new File(Environment.getExternalStorageDirectory().getAbsolutePath(), fileName);
    private String audiofileName = "audio_"+dtf.format(now)+ ".amr";
    //    private String audiofileName = "samplefile.jpg";
    File audiofile ;//= new File(Environment.getExternalStorageDirectory().getAbsolutePath(), audiofileName);


    private MediaRecorder mediaRecorder;
    private String userQuery;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP && checkSelfPermission(Manifest.permission.RECORD_AUDIO)!= PackageManager.PERMISSION_GRANTED){
            requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO},1000);
        }
        try {
            audiofile = new File(Environment.getExternalStorageDirectory().getAbsolutePath(), audiofileName);
            Log.e(LOG_TAG, "********** audio file name : *******"+audiofileName);
        } catch (Exception e) {
            Log.e(LOG_TAG, "********** Error saving! ********" + e.toString());
        }

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_start_survey);
        btnSpeak = (ImageButton) findViewById(R.id.btnSpeak);
        txtSpeechInput = (TextView) findViewById(R.id.txtSpeechInput);
        outputText = (TextView) findViewById(R.id.outputTex);

        Log.e(LOG_TAG,"Try TTS setting");
        textToSpeech=new TextToSpeech(getApplicationContext(), new TextToSpeech.OnInitListener() {
            @Override
            public void onInit(int status) {
                if(status!=TextToSpeech.ERROR) {
                    textToSpeech.setLanguage(new Locale("hi", "IN"));
                }
            }
        });
        Log.e(LOG_TAG,"Done TTS setting");

        Intent intent = getIntent();
        Log.e(LOG_TAG,"Try getStringExtra EXTRA_MESSAGE");
        String s_t = intent.getStringExtra(MainActivity.EXTRA_MESSAGE);
        Log.e(LOG_TAG,"Try getStringExtra SURVEY_NAME");
        Log.e(LOG_TAG, "Extra Message : "+s_t);

        String sn = intent.getStringExtra(MainActivity.SURVEY_NAME);
        setTitle(sn);

        if(sn== "Location Survey"){
            indexUrl = "https://9958ede63c0a.ngrok.io/intent/getanswer/";
//            indexUrl = "http://ec2-204-236-244-239.compute-1.amazonaws.com:8000/intent/getlocation/";
        }
        else if(sn=="Employment Survey"){
            indexUrl = "https://9958ede63c0a.ngrok.io/intent/getanswer/";
//            indexUrl = "http://ec2-204-236-244-239.compute-1.amazonaws.com:8000/intent/getlocation/";
        }
        String s = "";

//        JSONObject jObject = null;
//        try {
//            jObject = new JSONObject(s_t);
//            s = jObject.getString("message");
//        } catch (JSONException e) {
//            e.printStackTrace();
//            Log.e(LOG_TAG, e.toString());
//        }
        s = unescapeJava(s_t);
        int ques_idx_pos = s.indexOf("question_idx:");
        String ques_idx = s.substring(ques_idx_pos+14);
        s = s.substring(0,ques_idx_pos-2);
        Log.e(LOG_TAG, "Ques Idx :"+ques_idx);
        Log.e(LOG_TAG, "Processed string : "+s);
//        api_resp = unescapeJavaHealth(s_t);
        outputText.setText(s);
        a.setstring(s);
        f_ques_idx = ques_idx;
        System.out.println(s);
        saveTextAsFile("vaani:  " + s + '\n');
        Log.e(LOG_TAG, "Initial message:"+s);


        btnSpeak.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                promptSpeechInput();
            }
        });
    }
    private void promptSpeechInput() {
        Log.e(LOG_TAG,"******************Wohoo reached here******************");
        String q=a.y;
        Log.e(LOG_TAG, q);
        if(q.indexOf("question_idx")!=-1) {
            int ques_idx_pos = q.indexOf("question_idx");
            String ques_idx = q.substring(ques_idx_pos + 15, q.length()-1);
            q = q.substring(0, ques_idx_pos - 2);
            Log.e(LOG_TAG, "Ques Idx :" + ques_idx);
            Log.e(LOG_TAG, "Processed string : " + q);
            outputText.setText(q);
            a.setstring(q);
            f_ques_idx = ques_idx;
            Log.e(LOG_TAG, "FQUES IDX : "+f_ques_idx);
        }
        CharSequence first_message = a.y;
        Log.e(LOG_TAG,"################## Message ###############");
//            textToSpeech.speak(q,TextToSpeech.QUEUE_FLUSH,null);
        textToSpeech.speak(first_message, TextToSpeech.QUEUE_FLUSH, null, null);
        Log.e(LOG_TAG,"################## Message 1 ###############");
        try {
            double x= 0.0;
            if(q!=null)x=4*((double)q.length()/52);
            System.out.println(x);
            TimeUnit.SECONDS.sleep((long) x);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        String languagePref = "hi";
        Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
        intent.putExtra("android.speech.extra.GET_AUDIO_FORMAT", "audio/AMR");
        intent.putExtra("android.speech.extra.GET_AUDIO", true);
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, languagePref);
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE, languagePref);
        intent.putExtra(RecognizerIntent.EXTRA_ONLY_RETURN_LANGUAGE_PREFERENCE, languagePref);
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
        intent.putExtra(RecognizerIntent.EXTRA_PROMPT,
                "Say Something");
        try {
//            setupMediaRecorder();
//            try{
//                mediaRecorder.prepare();
//                mediaRecorder.start();
//            }
//            catch (IOException e){
//                Log.e(LOG_TAG,e.getMessage());
//            }
            startActivityForResult(intent, REQ_CODE_SPEECH_INPUT);
        } catch (ActivityNotFoundException a) {
            Toast.makeText(getApplicationContext(),
                    "sorry! Your device doesn't support speech input",
                    Toast.LENGTH_SHORT).show();
        }
    }

    public static String unescapeJava(String escaped) {

        if (escaped.indexOf("\\u") == -1)
            return escaped;

        String processed = "";

        int position = escaped.indexOf("\\u");
        while (position != -1) {
            if (position != 0)
                processed += escaped.substring(0, position);
            String token = escaped.substring(position + 2, position + 6);
            escaped = escaped.substring(position + 6);
            processed += (char) Integer.parseInt(token, 16);
            position = escaped.indexOf("\\u");
        }
        processed += escaped;

        processed = processed.replace("संदेश","");
        processed = processed.replace("&quot;","");
        processed = processed.replace("&quot;:","");
        Log.e(LOG_TAG, "Health Primary processed string : "+processed);
        processed = processed.substring(2,processed.length()-1);
        return processed;
    }

    private void setupMediaRecorder() {
        mediaRecorder = new MediaRecorder();
        mediaRecorder.setAudioSource(MediaRecorder.AudioSource.MIC);
        mediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.THREE_GPP);
        mediaRecorder.setOutputFile(audiofileName);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
//        mediaRecorder.stop();

        switch (requestCode) {
            case REQ_CODE_SPEECH_INPUT: {
                if (resultCode == RESULT_OK && null != data) {

                    ArrayList<String> result = data
                            .getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
                    userQuery=result.get(0);

                    txtSpeechInput.setText(userQuery);
//                    startConnection task=new startConnection();
//                    task.execute(userQuery);
                    saveTextAsFile("user:  "+userQuery+'\n');

                    Uri audioUri = data.getData();
                    ContentResolver contentResolver = getContentResolver();
                    try {
                        Log.e(LOG_TAG, audioUri.toString());
                        InputStream filestream = contentResolver.openInputStream(audioUri);
                        FileUtils.copyInputStreamToFile(filestream,audiofile);
                        startConnection task=new startConnection();
                        task.execute(userQuery);
//                        System.out.println("====="+f_ques_idx+"=====");
                    } catch (FileNotFoundException e) {
                        Log.e(LOG_TAG, "File not found!" + e.toString());
                    } catch (IOException e) {
                        Log.e(LOG_TAG, "Error saving!" + e.toString());
                    }
                }
                break;
            }
        }
    }

    private void saveTextAsFile(String s) {
        try{
            FileOutputStream fos = new FileOutputStream(file,true);
            fos.write(s.getBytes());
            fos.close();
            //Toast.makeText(this,"Saved!",Toast.LENGTH_SHORT).show();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
            //Toast.makeText(this,"File not found!",Toast.LENGTH_SHORT).show();
        } catch (IOException e) {
            e.printStackTrace();
            //Toast.makeText(this,"Error saving!",Toast.LENGTH_SHORT).show();
        }
    }

    class startConnection extends AsyncTask<String, Void, String> {
        @Override
        protected String doInBackground(String... voids) {
            String s = null;
            try {
                Instant start = Instant.now();
                s = GetText(voids[0]);
                Instant finish = Instant.now();
                long timeElapsed = Duration.between(start, finish).toMillis();
                System.out.println(timeElapsed);
            } catch (UnsupportedEncodingException e) {





                e.printStackTrace();
                Log.e("karma", "Exception occurred " + e);
            }
            return s;
        }
        @Override
        protected void onPostExecute(String s_t) {
            String s = unescapeJava(s_t);

            super.onPostExecute(s);
            outputText.setText(StringEscapeUtils.unescapeJava(s));


            Log.e(LOG_TAG,s);
            a.setstring(s);
            if(s=="");
            else {
                promptSpeechInput();
            }
            saveTextAsFile("vaani:  " + " संदेश" + s + '\n');

        }
    }
    public String GetText(String query) throws UnsupportedEncodingException {
        //====================================//
        String requestURL = "http://ec2-54-146-209-111.compute-1.amazonaws.com/vsurvey/get_entity/";
//        String requestURL = "http://ec2-204-236-244-239.compute-1.amazonaws.com:8000/intent/getlocation/";
        String charset = "UTF-8";
        String TAG = " URLConnection";
        String responseString = "";

        String dir = Environment.getExternalStorageDirectory()+File.separator+"ankitsDirectory";
        File folder = new File(dir); //folder name
//        File myfile = new File(dir, "myfile.txt");
        String filename = audiofile.getAbsolutePath();
        File file_to_send = new File(filename);


        MultipartUtility multipart;
        try {
            multipart = new MultipartUtility(requestURL, charset);

            // In your case you are not adding form data so ignore this
            /*This is to add parameter values */
            //        for (int i = 0; i < myFormDataArray.size(); i++) {
            //            multipart.addFormField(myFormDataArray.get(i).getParamName(),
            //                    myFormDataArray.get(i).getParamValue());
            //        }
            multipart.addFormField("question_idx", f_ques_idx);
            multipart.addFormField("answer", userQuery);
            Log.e(LOG_TAG, "**** Filename in API response : ****"+filename);
            multipart.addFilePart("file1", file_to_send);


            //add your file here.
            /*This is to add file content*/
            //        for (int i = 0; i < myFileArray.size(); i++) {
            //            multipart.addFilePart(myFileArray.getParamName(),
            //                    new File(myFileArray.getFileName()));
            //        }

            List<String> response = multipart.finish();
            Log.e(LOG_TAG, "After server reply : "+response);
            Log.e(TAG, "SERVER REPLIED:");

            StringBuilder sb = new StringBuilder();

            for (String line : response) {
                Log.e(TAG, "Upload Files Response:::" + line);
                // get your server response here.s
                sb.append(line + '\n');

                responseString = line;
            }

            String text = sb.toString();
            Log.e(TAG, "Total Response:::" + text);

            return text;
        } catch (IOException e) {
            Log.e(TAG, "IOException:::" + e.getMessage());
            //  e.printStackTrace();
            return null;
        }
    }
}
