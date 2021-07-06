package com.example.voicesurvey;

import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.text.Html;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;

import java.io.File;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.concurrent.ExecutionException;

@RequiresApi(api = Build.VERSION_CODES.O)
public class MainActivity extends AppCompatActivity {
    public static final String EXTRA_MESSAGE = "com.example.myfirstapp.MESSAGE";
    public static final String SURVEY_NAME = "com.example.myfirstapp.SURVEYMESSAGE";
    private static final String LOG_TAG = "Main Activity";


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP && checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE)!= PackageManager.PERMISSION_GRANTED){
            requestPermissions(new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE},1000);
        }
//        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP && checkSelfPermission(Manifest.permission.RECORD_AUDIO)!= PackageManager.PERMISSION_GRANTED){
//            requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO},1000);
//        }

        setTitle("Survey Application");
    }
    public void sendMessage(View view) throws UnsupportedEncodingException, ExecutionException, InterruptedException {
        String s =
                new setupConnectionTask()
                        .execute()
                        .get();
        String sn = "Employment Survey";
        Log.e(LOG_TAG,"******************Wohoo reached here******************");
        Log.e(LOG_TAG,"Employment Survey");
        Intent intent = new Intent(this, startSurvey.class);
        intent.putExtra(EXTRA_MESSAGE, TextUtils.htmlEncode(s));
        intent.putExtra(SURVEY_NAME, sn);
        startActivity(intent);
    }
    public void sendMessage2(View view) throws UnsupportedEncodingException, ExecutionException, InterruptedException {
        String s =
                new setupConnectionTask()
                        .execute()
                        .get();
        String sn = "Location Survey";
        Log.e(LOG_TAG,"Location Survey");
        Intent intent = new Intent(this, startSurvey.class);
        intent.putExtra(EXTRA_MESSAGE, s);
        intent.putExtra(SURVEY_NAME, sn);
        startActivity(intent);
    }

    public void sendMessageHealth(View view) throws UnsupportedEncodingException, ExecutionException, InterruptedException {
        String s =
                new setupHealthConnectionTask()
                        .execute()
                        .get();
        String sn = "Health Survey";
        // Log.e(LOG_TAG,"******************Wohoo reached here******************");
        // Log.e(LOG_TAG,"Health Survey");
        Intent intent = new Intent(this, startSurvey.class);
        intent.putExtra(EXTRA_MESSAGE, TextUtils.htmlEncode(s));
        intent.putExtra(SURVEY_NAME, sn);
        startActivity(intent);
    }

    class setupConnectionTask extends AsyncTask<String, Void, String> {
        @Override
        protected String doInBackground(String... voids) {
            String s = null;
            try {
                Log.e(LOG_TAG,"Try Setup Connection");
                Instant start = Instant.now();
                s = setupConnection("Name_Survey");
                Log.e(LOG_TAG,"Done Setup Connection");
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
        protected void onPostExecute(String s) {
            super.onPostExecute(s);
        }
    }

    class setupHealthConnectionTask extends AsyncTask<String, Void, String> {
        @Override
        protected String doInBackground(String... voids) {
            String s = null;
            try {
                Log.e(LOG_TAG,"Try Setup Health Connection");
                Instant start = Instant.now();
                s = setupHealthConnection();
                Log.e(LOG_TAG,"Done Setup Connection");
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
        protected void onPostExecute(String s) {
            super.onPostExecute(s);
        }
    }

    public String setupConnection(String query) throws UnsupportedEncodingException {
        //====================================//
        String requestURL = "https://7d1e3fffc8ea.ngrok.io/intent/conn/";
//        String requestURL = "http://ec2-204-236-244-239.compute-1.amazonaws.com:8000/intent/conn/";
        String charset = "UTF-8";
        String TAG = "URLConnection";
        String responseString = "";

        Log.e(LOG_TAG,"Try Directory Setup");
        String dir = Environment.getExternalStorageDirectory()+ File.separator+"ankitsDirectory";
        File folder = new File(dir); //folder name
        Log.e(LOG_TAG,"Done Directory Setup");


        MultipartUtility multipart;
        try {
            multipart = new MultipartUtility(requestURL, charset);

            // In your case you are not adding form data so ignore this
            /*This is to add parameter values */
            Log.e(LOG_TAG,"Try Multipart setting");
            multipart.addFormField("survey", query);

            List<String> response = multipart.finish();
            Log.e(TAG, "SERVER REPLIED:");
            for (String line : response) {
                Log.e(TAG, "Upload Files Response:::" + line);
                // get your server response here.
                responseString = line;
            }
            Log.e(LOG_TAG,"Done Multipart setting");
            return responseString;
        } catch (IOException e) {
            Log.e(TAG, "IOException:::" + e.getMessage());
            //  e.printStackTrace();
            return null;
        }
    }

    public String setupHealthConnection() throws UnsupportedEncodingException {
        //====================================//
        String requestURL = "http://ec2-54-146-209-111.compute-1.amazonaws.com/vsurvey/est_conn/";
//        String requestURL = "http://ec2-204-236-244-239.compute-1.amazonaws.com:8000/intent/conn/";
        String charset = "UTF-8";
        String TAG = "URLConnection";
        String responseString = "";

        Log.e(LOG_TAG,"Try Directory Setup");
        String dir = Environment.getExternalStorageDirectory()+ File.separator+"ankitsDirectory";
        File folder = new File(dir); //folder name
        Log.e(LOG_TAG,"Done Directory Setup");


        MultipartUtility multipart;
        try {
            multipart = new MultipartUtility(requestURL, charset);

            // In your case you are not adding form data so ignore this
            /*This is to add parameter values */
            Log.e(LOG_TAG,"Try Multipart setting");
//            multipart.addFormField("survey", query);

            List<String> response = multipart.finish();
            Log.e(TAG, "HEALTH SERVER REPLIED:");
            for (String line : response) {
                Log.e(TAG, "Upload Files Response:::" + line);
                // get your server response here.
                responseString = line;
            }
            Log.e(LOG_TAG,"Done Multipart setting");
            return responseString;
        } catch (IOException e) {
            Log.e(TAG, "IOException:::" + e.getMessage());
            //  e.printStackTrace();
            return null;
        }
    }
}

