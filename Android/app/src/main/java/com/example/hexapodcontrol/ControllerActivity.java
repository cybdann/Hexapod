package com.example.hexapodcontrol;

import android.annotation.SuppressLint;
import android.app.Dialog;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.graphics.drawable.Drawable;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
import android.view.Window;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.ViewFlipper;

import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;

import com.airbnb.lottie.LottieAnimationView;

import org.eclipse.paho.client.mqttv3.MqttException;

import java.util.Objects;

public class ControllerActivity extends AppCompatActivity implements JoystickView.JoystickListener {

    private LottieAnimationView batteryLevel;
    private static MQTTModule mqttModule;

    private final static String URI = "tcp://172.16.0.104:1883";
    private final static String TAG = "JoystickActivity";

    private final Handler handler = new Handler();

    private boolean dlp = false;

    // Boolean variables for st
    private boolean stopThread = false;
    private boolean showDialogBATTERY = false;

    // Save switch states
    private boolean showGyro = true;
    private boolean showSpeedometer = true;
    private boolean showLefLegLEDS = true;
    private boolean showRightLegLEDS = true;
    private boolean showStatuses = true;

    // Face button modes
    private boolean modeA = true;         // Default control mode
    private boolean modeB = false;
    private boolean isESCOn = true;       // ESC is ON by default, OFF when mode B is selected
    private boolean isSitting = true;

    // Alerts
    private Dialog dialogMQTT;
    private Dialog dialogWAITING;
    private Dialog dialogSTATUS;
    private Dialog dialogBATTERY;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_controller);
        Objects.requireNonNull(getSupportActionBar()).hide();

        // Hide the status bar
        View decorView = getWindow().getDecorView();
        int uiOptions = View.SYSTEM_UI_FLAG_FULLSCREEN;
        decorView.setSystemUiVisibility(uiOptions);

        // Init controller views
        initDPads();
        initFaceButtons();
        initBatteryLevel();
        initSensors();

        // Check MQTT network connection
        dialogMQTT = alertMQTT();
        dialogSTATUS = alertWAITING();
        dialogBATTERY = alertBATTERY();

        mqttModule = new MQTTModule(URI);
        mqttModule.createClient(this);

        // Subscribe to topics
        String[] topics = {"BATLVL", "SX", "READY"};
        mqttModule.subscribeToTopic(topics, 1);

        // Check MQTT connection
        MQTTCheckConnection checkConnection = new MQTTCheckConnection();
        new Thread(checkConnection).start();

        // Check for incoming subscription messages
        MQTTSubscriptions checkSubscriptions = new MQTTSubscriptions();
        new Thread(checkSubscriptions).start();

        // Waiting for the Hexapod to be ready

        handler.post(() -> {
            dialogSTATUS.show();

            // Hide the status bar.
            View decorView1 = getWindow().getDecorView();
            int uiOptions1 = View.SYSTEM_UI_FLAG_FULLSCREEN;
            decorView1.setSystemUiVisibility(uiOptions1);
        });

    }

    public boolean isInternetAvailable() {
        ConnectivityManager cm = (ConnectivityManager) this.getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo netInfo = cm.getActiveNetworkInfo();
        return netInfo == null || !netInfo.isConnectedOrConnecting();
    }

    @SuppressLint({"DefaultLocale", "SetTextI18n"})
    @Override
    public void onJoystickMoved(float xPercent, float yPercent, String ID) {
        Log.d(TAG, ID + " X: " + String.format("%.1f", xPercent / 100) + " Y : " + yPercent);

        if(ID.equals("R")) {
            runOnUiThread(new Runnable() {
                final TextView statusMotion = findViewById(R.id.statusMotion);

                @Override
                public void run() {
                    final boolean b = Math.round(xPercent) != 0 || Math.round(yPercent) != 0;

                    if(modeA && b) {
                        statusMotion.setText("Walking");
                    }
                    else if(modeB && b){
                        statusMotion.setText("Changing pitch");
                    }
                    else {
                        statusMotion.setText("Standing by");
                    }
                }
            });
        }
        else {
            runOnUiThread(new Runnable() {
                final TextView statusMotion = findViewById(R.id.statusMotion);

                @Override
                public void run() {
                    final boolean b = Math.round(xPercent) != 0 || Math.round(yPercent) != 0;

                    if(modeA && b) {
                        statusMotion.setText("Rotating");
                    }
                    else if(modeB && b){
                        statusMotion.setText("Changing yaw");
                    }
                    else {
                        statusMotion.setText("Standing by");
                    }
                }
            });
        }

        if(isInternetAvailable()) {
            try {
                mqttModule.getClient().disconnect();
            } catch (MqttException e) {
                e.printStackTrace();
            }

            Intent intent = new Intent(this, MenuActivity.class);
            this.finish();
            overridePendingTransition(0, android.R.anim.fade_out);
            startActivity(intent);
        }

        mqttModule.publishMessage(ID, String.format("%.1f", xPercent / 100) + "," + String.format("%.1f", -(yPercent / 100)), 0, true);
    }

    @Override
    public void onBackPressed() {
        super.onBackPressed();

        stopThread = true;

        try {
            mqttModule.getClient().disconnect();
        } catch (MqttException e) {
            e.printStackTrace();
        }

        Intent intent = new Intent(this, MenuActivity.class);
        this.finish();

        overridePendingTransition(0, android.R.anim.fade_out);
        startActivity(intent);
    }

    @SuppressLint({"SetTextI18n", "ClickableViewAccessibility", "UseCompatLoadingForDrawables"})
    public void stopStartServos(View v) {
        Button bt_stop_start = findViewById(R.id.bt_stop_start);

        if(isInternetAvailable()) {
            try {
                mqttModule.getClient().disconnect();
            } catch (MqttException e) {
                e.printStackTrace();
            }

            Intent intent = new Intent(this, MenuActivity.class);
            this.finish();
            overridePendingTransition(0, android.R.anim.fade_out);
            startActivity(intent);
        }

        bt_stop_start.setOnTouchListener((view, motionEvent) -> {

            if(motionEvent.getAction() == MotionEvent.ACTION_DOWN) {
                bt_stop_start.setBackground(getResources().getDrawable(R.drawable.button_a_shaded));
                mqttModule.publishMessage("SM", "1", 1, false);
            } else if (motionEvent.getAction() == MotionEvent.ACTION_UP) {
                bt_stop_start.setBackground(getResources().getDrawable(R.drawable.button_a));
            }

            return false;
        });


    }

    @SuppressLint({"ClickableViewAccessibility", "UseCompatLoadingForDrawables", "SetTextI18n"})
    public void initFaceButtons() {
        Button bt_face_X = findViewById(R.id.bt_face_X);
        Button bt_face_Y = findViewById(R.id.bt_face_Y);
        Button bt_face_A = findViewById(R.id.bt_face_A);
        Button bt_face_B = findViewById(R.id.bt_face_B);
        Button bt_face_C = findViewById(R.id.bt_face_C);
        Button bt_face_T = findViewById(R.id.bt_face_T);

        TextView textWalkingStatus = findViewById(R.id.statusWalkingMode);
        TextView textFaceModeStatus = findViewById(R.id.statusFaceMode);
        TextView textMotionStatus = findViewById(R.id.statusMotion);

        bt_face_X.setOnTouchListener((view, motionEvent) -> {

            if(motionEvent.getAction() == MotionEvent.ACTION_DOWN) {
                textWalkingStatus.setText("Tripod gait");

                bt_face_X.setBackground(getResources().getDrawable(R.drawable.button_x_shaded));
                mqttModule.publishMessage("GAIT", "TR", 0, false);
            } else if (motionEvent.getAction() == MotionEvent.ACTION_UP) {
                bt_face_X.setBackground(getResources().getDrawable(R.drawable.button_x));
            }

            return false;
        });

        bt_face_Y.setOnTouchListener((view, motionEvent) -> {

            if(motionEvent.getAction() == MotionEvent.ACTION_DOWN) {
                textWalkingStatus.setText("Metachronal gait");

                bt_face_Y.setBackground(getResources().getDrawable(R.drawable.button_y_shaded));
                mqttModule.publishMessage("GAIT", "MT", 0, false);
            } else if (motionEvent.getAction() == MotionEvent.ACTION_UP) {
                bt_face_Y.setBackground(getResources().getDrawable(R.drawable.button_y));
            }

            return false;
        });

        bt_face_A.setOnTouchListener((view, motionEvent) -> {

            if(motionEvent.getAction() == MotionEvent.ACTION_DOWN) {
                modeA = !modeA;
                if(modeA) {
                    modeB = false;
                }
                textFaceModeStatus.setText("A mode selected");

                bt_face_A.setBackground(getResources().getDrawable(R.drawable.button_a_shaded));
                mqttModule.publishMessage("MODE", "A", 0, false);
            } else if (motionEvent.getAction() == MotionEvent.ACTION_UP) {
                bt_face_A.setBackground(getResources().getDrawable(R.drawable.button_a));
            }

            return false;
        });

        bt_face_B.setOnTouchListener((view, motionEvent) -> {

            if(motionEvent.getAction() == MotionEvent.ACTION_DOWN) {
                modeB = !modeB;
                if(modeB) {
                    modeA = false;
                }
                textFaceModeStatus.setText("B mode selected");

                bt_face_B.setBackground(getResources().getDrawable(R.drawable.button_b_shaded));
                mqttModule.publishMessage("MODE", "B", 0, false);
            } else if (motionEvent.getAction() == MotionEvent.ACTION_UP) {
                bt_face_B.setBackground(getResources().getDrawable(R.drawable.button_b));
            }

            return false;
        });

        bt_face_C.setOnTouchListener(new View.OnTouchListener() {
            final String ID = getResources().getResourceEntryName(bt_face_C.getId());
            final String topic = ID.substring(ID.length() - 1);

            @Override
            public boolean onTouch(View view, MotionEvent motionEvent) {

                if(motionEvent.getAction() == MotionEvent.ACTION_DOWN) {
                    isESCOn = !isESCOn;

                    if(isESCOn) {
                        bt_face_C.setBackground(getResources().getDrawable(R.drawable.button_esc));
                        mqttModule.publishMessage("SE", "1", 1, false); // Status publish
                    }
                    else {
                        bt_face_C.setBackground(getResources().getDrawable(R.drawable.button_a));
                        mqttModule.publishMessage("SE", "0", 1, false); // Status publish
                    }
                    mqttModule.publishMessage(topic, "1", 0, false);
                }

                return false;
            }
        });

        bt_face_T.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View view, MotionEvent motionEvent) {

                if(motionEvent.getAction() == MotionEvent.ACTION_DOWN) {
                    isSitting = !isSitting;
                    Button bt = findViewById(R.id.bt_face_T);

                    if(!isSitting) {
                        bt_face_T.setBackground(getResources().getDrawable(R.drawable.button_sit));
                        mqttModule.publishMessage("SS", "1", 1, false); // Status publish
                        textMotionStatus.setText("Standing by");
                        bt.setText("SIT");
                    }
                    else {
                        bt_face_T.setBackground(getResources().getDrawable(R.drawable.button_up));
                        mqttModule.publishMessage("SS", "0", 1, false); // Status publish
                        textMotionStatus.setText("Sitting");

                        bt.setText("UP");
                    }

                    handler.post(() -> dialogSTATUS.show());
                }

                return false;
            }
        });
    }

    @SuppressLint({"ClickableViewAccessibility", "UseCompatLoadingForDrawables"})
    public void initDPads() {
        Button bt_dpad_DU = findViewById(R.id.bt_dpad_DU);
        Button bt_dpad_DR = findViewById(R.id.bt_dpad_DR);
        Button bt_dpad_DD = findViewById(R.id.bt_dpad_DD);
        Button bt_dpad_DL = findViewById(R.id.bt_dpad_DL);

        bt_dpad_DU.setOnTouchListener(new View.OnTouchListener() {
            final String ID = getResources().getResourceEntryName(bt_dpad_DU.getId());
            final String topic = ID.substring(ID.length() - 2);

            @Override
            public boolean onTouch(View view, MotionEvent motionEvent) {

                if(motionEvent.getAction() == MotionEvent.ACTION_DOWN) {
                    bt_dpad_DU.setBackground(getResources().getDrawable(R.drawable.arrow_shape_shaded));
                    dlp = true;
                    DPadLongPress dpadLongPress = new DPadLongPress(topic);
                    new Thread(dpadLongPress).start();
                } else if (motionEvent.getAction() == MotionEvent.ACTION_UP) {
                    bt_dpad_DU.setBackground(getResources().getDrawable(R.drawable.arrow_shape));
                    dlp = false;
                }

                return false;
            }
        });

        bt_dpad_DR.setOnTouchListener(new View.OnTouchListener() {
            final String ID = getResources().getResourceEntryName(bt_dpad_DR.getId());
            final String topic = ID.substring(ID.length() - 2);

            @Override
            public boolean onTouch(View view, MotionEvent motionEvent) {

                if(motionEvent.getAction() == MotionEvent.ACTION_DOWN) {
                    bt_dpad_DR.setBackground(getResources().getDrawable(R.drawable.arrow_shape_shaded));
                    dlp = true;
                    DPadLongPress dpadLongPress = new DPadLongPress(topic);
                    new Thread(dpadLongPress).start();
                } else if (motionEvent.getAction() == MotionEvent.ACTION_UP) {
                    bt_dpad_DR.setBackground(getResources().getDrawable(R.drawable.arrow_shape));
                    dlp = false;
                }

                return false;
            }
        });

        bt_dpad_DD.setOnTouchListener(new View.OnTouchListener() {
            final String ID = getResources().getResourceEntryName(bt_dpad_DD.getId());
            final String topic = ID.substring(ID.length() - 2);

            @Override
            public boolean onTouch(View view, MotionEvent motionEvent) {

                if(motionEvent.getAction() == MotionEvent.ACTION_DOWN) {
                    bt_dpad_DD.setBackground(getResources().getDrawable(R.drawable.arrow_shape_shaded));
                    dlp = true;
                    DPadLongPress dpadLongPress = new DPadLongPress(topic);
                    new Thread(dpadLongPress).start();
                } else if (motionEvent.getAction() == MotionEvent.ACTION_UP) {
                    bt_dpad_DD.setBackground(getResources().getDrawable(R.drawable.arrow_shape));
                    dlp = false;
                }

                return false;
            }
        });

        bt_dpad_DL.setOnTouchListener(new View.OnTouchListener() {
            final String ID = getResources().getResourceEntryName(bt_dpad_DL.getId());
            final String topic = ID.substring(ID.length() - 2);

            @Override
            public boolean onTouch(View view, MotionEvent motionEvent) {

                if(motionEvent.getAction() == MotionEvent.ACTION_DOWN) {
                    bt_dpad_DL.setBackground(getResources().getDrawable(R.drawable.arrow_shape_shaded));
                    dlp = true;
                    DPadLongPress dpadLongPress = new DPadLongPress(topic);
                    new Thread(dpadLongPress).start();
                } else if (motionEvent.getAction() == MotionEvent.ACTION_UP) {
                    bt_dpad_DL.setBackground(getResources().getDrawable(R.drawable.arrow_shape));
                    dlp = false;
                }

                return false;
            }
        });
    }

    public void initBatteryLevel() {
        batteryLevel = findViewById(R.id.lottie_battery_level);

        // From 0% to 100% batter level
        batteryLevel.setFrame(100);
        batteryLevel.setMinAndMaxFrame(0, 100);
    }

    public void initSensors() {
        ImageView level_ball = findViewById(R.id.level_ball);

        // Convert from dp to px
        float scale = level_ball.getContext().getResources().getDisplayMetrics().density;
        int dps = 40;
        int pixels = (int) (dps * scale + 0.5f);

        level_ball.setY(pixels);
    }

    public Dialog alertMQTT() {
        final Dialog dialog = new Dialog(this);

        // Hide the status bar.
        View decorView = dialog.getWindow().getDecorView();
        int uiOptions = View.SYSTEM_UI_FLAG_FULLSCREEN;
        decorView.setSystemUiVisibility(uiOptions);

        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE);
        dialog.setCancelable(false);
        dialog.setContentView(R.layout.alert_connecting);

        dialog.getWindow().setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));

        return dialog;
    }

    public Dialog alertWAITING() {
        final Dialog dialog = new Dialog(this);

        // Hide the status bar.
        View decorView = dialog.getWindow().getDecorView();
        int uiOptions = View.SYSTEM_UI_FLAG_FULLSCREEN;
        decorView.setSystemUiVisibility(uiOptions);

        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE);
        dialog.setCancelable(false);
        dialog.setContentView(R.layout.alert_sitting);

        dialog.getWindow().setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));

        return dialog;
    }

    public Dialog alertBATTERY() {
        Dialog dialog = new Dialog(this);

        // Hide the status bar.
        View decorView = dialog.getWindow().getDecorView();
        int uiOptions = View.SYSTEM_UI_FLAG_FULLSCREEN;
        decorView.setSystemUiVisibility(uiOptions);

        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE);
        dialog.setCancelable(true);
        dialog.setContentView(R.layout.alert_battery);
        dialog.getWindow().setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));

        Button dialogButton = dialog.findViewById(R.id.btn_dialog);

        dialogButton.setOnClickListener(v -> {
            dialog.dismiss();

            // Hide the status bar.
            View decorView1 = getWindow().getDecorView();
            int uiOptions1 = View.SYSTEM_UI_FLAG_FULLSCREEN;
            decorView1.setSystemUiVisibility(uiOptions1);
        });

        return dialog;
    }

    public void showInstructions(View v){
        final Dialog dialog = new Dialog(this);

        // Hide the status bar.
        View decorView = dialog.getWindow().getDecorView();
        int uiOptions = View.SYSTEM_UI_FLAG_FULLSCREEN;
        decorView.setSystemUiVisibility(uiOptions);

        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE);
        dialog.setCancelable(false);
        dialog.setContentView(R.layout.dialog_instructions);

        ViewFlipper viewFlipper = dialog.findViewById(R.id.vf_instructions);
        Button dialogButton = dialog.findViewById(R.id.btn_dialog);
        LottieAnimationView next = dialog.findViewById(R.id.lottie_next);
        LottieAnimationView prev = dialog.findViewById(R.id.lottie_prev);

        dialogButton.setOnClickListener(v1 -> {
            dialog.dismiss();

            // Hide the status bar.
            View decorView1 = getWindow().getDecorView();
            int uiOptions1 = View.SYSTEM_UI_FLAG_FULLSCREEN;
            decorView1.setSystemUiVisibility(uiOptions1);
        });

        next.setOnClickListener(v12 -> viewFlipper.showNext());

        prev.setOnClickListener(v13 -> viewFlipper.showPrevious());

        dialog.getWindow().setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
        dialog.show();
    }

    @SuppressLint("UseSwitchCompatOrMaterialCode")
    public void showSettings(View view) {
        final Dialog dialog = new Dialog(this);

        // Hide the status bar.
        View decorView = dialog.getWindow().getDecorView();
        int uiOptions = View.SYSTEM_UI_FLAG_FULLSCREEN;
        decorView.setSystemUiVisibility(uiOptions);

        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE);
        dialog.setCancelable(true);
        dialog.setContentView(R.layout.dialog_settings);

        Button dialogButton = dialog.findViewById(R.id.btn_dialog);

        Switch switchGryo = dialog.findViewById(R.id.switchGyro);
        Switch switchSpeedometer = dialog.findViewById(R.id.switchSpeedometer);
        Switch switchLeftLegLEDS = dialog.findViewById(R.id.switchLeftLegLeds);
        Switch switchRightLegLEDS = dialog.findViewById(R.id.switchRightLeds);
        Switch switchStatuses = dialog.findViewById(R.id.switchStatuses);

        dialogButton.setOnClickListener(v -> {
            dialog.dismiss();

            // Hide the status bar.
            View decorView1 = getWindow().getDecorView();
            int uiOptions1 = View.SYSTEM_UI_FLAG_FULLSCREEN;
            decorView1.setSystemUiVisibility(uiOptions1);
        });

        // Set the last states of the switches
        switchGryo.setChecked(showGyro);
        switchSpeedometer.setChecked(showSpeedometer);
        switchLeftLegLEDS.setChecked(showLefLegLEDS);
        switchRightLegLEDS.setChecked(showRightLegLEDS);
        switchStatuses.setChecked(showStatuses);

        // Set listeners for the switches
        switchGryo.setOnCheckedChangeListener((buttonView, isChecked) -> {
            View v = findViewById(R.id.gyroLayout);

            if (isChecked) {
                showGyro = true;
                v.setVisibility(View.VISIBLE);
            }
            else {
                showGyro = false;
                v.setVisibility(View.INVISIBLE);
            }
        });
        switchSpeedometer.setOnCheckedChangeListener((buttonView, isChecked) -> {
            View v = findViewById(R.id.speedometerLayout);

            if (isChecked) {
                showSpeedometer = true;
                v.setVisibility(View.VISIBLE);
            }
            else {
                showSpeedometer = false;
                v.setVisibility(View.INVISIBLE);
            }
        });
        switchLeftLegLEDS.setOnCheckedChangeListener((buttonView, isChecked) -> {
            View v = findViewById(R.id.leftLegLedsLayout);

            if (isChecked) {
                showLefLegLEDS = true;
                v.setVisibility(View.VISIBLE);
            }
            else {
                showLefLegLEDS = false;
                v.setVisibility(View.INVISIBLE);
            }
        });
        switchRightLegLEDS.setOnCheckedChangeListener((buttonView, isChecked) -> {
            View v = findViewById(R.id.rightLegLedsLayout);

            if (isChecked) {
                showRightLegLEDS = true;
                v.setVisibility(View.VISIBLE);
            }
            else {
                showRightLegLEDS = false;
                v.setVisibility(View.INVISIBLE);
            }
        });
        switchStatuses.setOnCheckedChangeListener((buttonView, isChecked) -> {
            View v = findViewById(R.id.statusesLayout);

            if (isChecked) {
                showStatuses = true;
                v.setVisibility(View.VISIBLE);
            }
            else {
                showStatuses = false;
                v.setVisibility(View.INVISIBLE);
            }
        });

        dialog.getWindow().setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
        dialog.show();
    }

    class MQTTCheckConnection implements Runnable{
        private boolean shown = false;

        MQTTCheckConnection() {

        }

        @Override
        public void run() {

            while(true) {
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }

                if(stopThread) {
                    return;
                }

                // Is not connected, show dialogMQTT
                if(!mqttModule.getClient().isConnected()) {
                    if(!shown) {
                        handler.post(() -> dialogMQTT.show());
                        shown = true;
                    }
                }
                // Is reconnected, dismiss the dialogMQTT
                else {
                    if(shown) {
                        handler.post(() -> {
                            dialogMQTT.dismiss();

                            // Hide the status bar.
                            View decorView = getWindow().getDecorView();
                            int uiOptions = View.SYSTEM_UI_FLAG_FULLSCREEN;
                            decorView.setSystemUiVisibility(uiOptions);
                        });
                    }

                    shown = false;
                }
            }
        }
    }

    class MQTTSubscriptions implements Runnable{
        MQTTSubscriptions() {

        }

        @RequiresApi(api = Build.VERSION_CODES.N)
        @Override
        public void run() {
            int level = 0;

            while(true) {
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }

                // Stop this thread in case of ...
                if(stopThread) {
                    return;
                }

                // Check for status update
                if(Objects.equals(mqttModule.getTopics().get("SX"), "1")) {
                    mqttModule.getTopics().replace("SX", "");

                    // Notify the user about the status of the Hexapod
                    handler.post(() -> {
                        dialogSTATUS.dismiss();

                        // Hide the status bar.
                        View decorView = getWindow().getDecorView();
                        int uiOptions = View.SYSTEM_UI_FLAG_FULLSCREEN;
                        decorView.setSystemUiVisibility(uiOptions);
                    });
                }
                else if(Objects.equals(mqttModule.getTopics().get("SX"), "0")) {
                    mqttModule.getTopics().replace("SX", "");

                    handler.post(() -> dialogSTATUS.show());

                }

                // Check for battery level
                try {
                    batteryLevel.setFrame(level);
                    level = Integer.parseInt(Objects.requireNonNull(mqttModule.getTopics().get("BATLVL")));

                    // Notify the user is the battery level drops below 20
                    if(level < 20 && !showDialogBATTERY) {
                        handler.post(() -> {
                            dialogBATTERY.show();
                            showDialogBATTERY = true;
                        });
                    }
                    else if(level > 20) {
                        showDialogBATTERY = false;
                    }

                } catch (NumberFormatException e) {
                    // If there is no battery level message yet
                    if(Objects.equals(mqttModule.getTopics().get("BATLVL"), "")) {
                        level = 20;
                        showDialogBATTERY = false;
                    }
                }

            }
        }
    }

    class DPadLongPress implements Runnable {
        String topic;

        DPadLongPress(String topic) {
            this.topic = topic;
        }

        @Override
        public void run() {
            while(dlp) {
                // Delay between messages
                try {
                    Thread.sleep(35);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }

                // Send dpad control message
                mqttModule.publishMessage(topic, "1", 0, false);
            }
        }
    }
}