package com.example.hexapodcontrol;

import androidx.appcompat.app.AppCompatActivity;

import android.app.Dialog;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.Bundle;
import android.os.Handler;
import android.view.View;
import android.view.Window;
import android.widget.Button;
import java.util.Objects;

public class MenuActivity extends AppCompatActivity {

    private static final int SPLASH_TIME_OUT = 1500;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_menu);
        Objects.requireNonNull(getSupportActionBar()).hide();

        // Hide the status bar.
        View decorView = getWindow().getDecorView();
        int uiOptions = View.SYSTEM_UI_FLAG_FULLSCREEN;
        decorView.setSystemUiVisibility(uiOptions);

        if(isInternetAvailable()) {
            showAlert();
        }

        Button bt_control = findViewById(R.id.bt_control);

        bt_control.setOnClickListener(v -> {
            if(isInternetAvailable()) {
                showAlert();

                // Hide the status bar.
                View decorView1 = getWindow().getDecorView();
                int uiOptions1 = View.SYSTEM_UI_FLAG_FULLSCREEN;
                decorView1.setSystemUiVisibility(uiOptions1);
            }
            else {
                setContentView(R.layout.activity_rotate_splash_screen);

                new Handler().postDelayed(() -> {
                    Intent menuIntent = new Intent(MenuActivity.this,  ControllerActivity.class);
                    startActivity(menuIntent);
                    finish();
                }, SPLASH_TIME_OUT);
            }
        });
    }

    public boolean isInternetAvailable() {
        ConnectivityManager cm = (ConnectivityManager) this.getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo netInfo = cm.getActiveNetworkInfo();
        return netInfo == null || !netInfo.isConnectedOrConnecting();
    }

    public void showAlert(){
        final Dialog dialog = new Dialog(this);
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE);
        dialog.setCancelable(false);
        dialog.setContentView(R.layout.alert_no_internet);

        Button dialogButton = dialog.findViewById(R.id.btn_dialog);
        dialogButton.setOnClickListener(v -> dialog.dismiss());

        dialog.getWindow().setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
        dialog.show();
    }
}