package com.example.hexapodcontrol;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.PixelFormat;
import android.graphics.PorterDuff;
import android.graphics.Typeface;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.View;

import androidx.core.content.res.ResourcesCompat;

public class JoystickView extends SurfaceView implements SurfaceHolder.Callback, View.OnTouchListener {

    private float currentX;
    private float currentY;
    private float centerX;
    private float centerY;
    private float baseRadius;
    private float hatRadius;

    private volatile boolean stopDragThread;
    private volatile boolean nonZeroValue;
    private JoystickListener joystickCallback;

    public JoystickView(Context context) {
        super(context);
        getHolder().addCallback(this);
        setOnTouchListener(this);

        if(context instanceof JoystickListener) {
            joystickCallback = (JoystickListener) context;
        }
    }

    public JoystickView(Context context, AttributeSet attributes, int style) {
        super(context, attributes, style);
        getHolder().addCallback(this);
        setOnTouchListener(this);

        if(context instanceof JoystickListener) {
            joystickCallback = (JoystickListener) context;
        }
    }

    public JoystickView(Context context, AttributeSet attributes) {
        super(context, attributes);
        // Canvas background color transparent
        this.setBackgroundColor(Color.TRANSPARENT);
        this.setZOrderOnTop(true);
        getHolder().setFormat(PixelFormat.TRANSPARENT);
        getHolder().addCallback(this);
        setOnTouchListener(this);

        if(context instanceof JoystickListener) {
            joystickCallback = (JoystickListener) context;
        }
    }

    private void drawJoystick(float newX, float newY, String ID) {
        if(getHolder().getSurface().isValid()) {
            Canvas myCanvas = this.getHolder().lockCanvas();
            Paint colors = new Paint();
            Typeface typeface = ResourcesCompat.getFont(getContext(), R.font.azonix);

            // Reset canvas after joystick use
            myCanvas.drawColor(Color.TRANSPARENT, PorterDuff.Mode.CLEAR);

            // Background circle color
            colors.setColor(Color.parseColor("#616161"));
            myCanvas.drawCircle(centerX, centerY, baseRadius, colors);

            // Movable circle color
            colors.setColor(Color.parseColor("#FF03DAC5"));
            myCanvas.drawCircle(newX, newY, hatRadius, colors);

            // Joystick ID
            colors.setColor(Color.parseColor("#FF000000"));
            colors.setTextSize((float) getHeight() / 5);
            colors.setTypeface(typeface);
            colors.setTextAlign(Paint.Align.CENTER);
            myCanvas.drawText(ID, newX, newY + 30, colors);

            getHolder().unlockCanvasAndPost(myCanvas);
        }
    }

    private void setupDimensions() {
        centerX = (float) getWidth() / 2;
        centerY = (float) getHeight() / 2;
        baseRadius = (float) Math.min(getWidth(), getHeight()) / 3;
        hatRadius = (float) Math.min(getWidth(), getHeight()) / 6;
    }

    @Override
    public void surfaceCreated(SurfaceHolder holder) {
        String ID = getResources().getResourceEntryName(getId());
        setupDimensions();
        drawJoystick(centerX, centerY, ID);
    }

    @Override
    public void surfaceChanged(SurfaceHolder holder, int format, int width, int height) {

    }

    @Override
    public void surfaceDestroyed(SurfaceHolder holder) {

    }



    @Override
    public boolean onTouch(View v, MotionEvent event) {
        String ID = getResources().getResourceEntryName(v.getId());

        if(v.equals(this)) {
            if(event.getAction() != MotionEvent.ACTION_UP) {
                stopDragThread = true;
                nonZeroValue = true;

                float displacement = (float) Math.sqrt(Math.pow(event.getX() - centerX, 2) + Math.pow(event.getY() - centerY, 2));

                if(displacement < baseRadius) {
                    drawJoystick(event.getX(), event.getY(), ID);
                    joystickCallback.onJoystickMoved((event.getX() - centerX) / baseRadius * 100, (event.getY() - centerY) / baseRadius * 100, ID);

                    currentX = event.getX();
                    currentY = event.getY();
                }
                else {
                    float ratio = baseRadius / displacement;
                    float constrainedX = centerX + (event.getX() - centerX) * ratio;
                    float constrainedY = centerY + (event.getY() - centerY) * ratio;

                    drawJoystick(constrainedX, constrainedY, ID);
                    joystickCallback.onJoystickMoved((constrainedX - centerX) / baseRadius * 100, (constrainedY - centerY) / baseRadius * 100, ID);

                    currentX = constrainedX;
                    currentY = constrainedY;
                }

            }
            else {
                    nonZeroValue = false;
                    stopDragThread = false;
                    DragThread dragThread = new DragThread(ID);
                    dragThread.start();
            }
        }

        return true;
    }

    public interface JoystickListener {
        void onJoystickMoved(float xPercent, float yPercent, String id);
    }

    class DragThread extends Thread {
        String joystickID;

        DragThread(String joystickID) {
            this.joystickID = joystickID;
        }

        @Override
        public void run() {
            float drag = (float) 5;

            while (!stopDragThread) {

                if (currentX - centerX > 0) {
                    currentX -= drag;
                } else {
                    currentX += drag;
                }

                if (currentY - centerY > 0) {
                    currentY -= drag;
                } else {
                    currentY += drag;
                }

                drawJoystick(currentX, currentY, joystickID);
                joystickCallback.onJoystickMoved((currentX - centerX) / baseRadius, (currentY - centerY) / baseRadius, joystickID);

                if (Math.abs(currentX - centerX) <= drag && Math.abs(currentY - centerY) <= drag) {
                    drawJoystick(centerX, centerY, joystickID);
                    joystickCallback.onJoystickMoved(0, 0, joystickID);
                    break;
                }
            }
        }
    }

    class NonZeroValueThread extends Thread {
        float xPercent;
        float yPercent;
        String ID;

        NonZeroValueThread(float xPercent, float yPercent, String ID) {
            this.xPercent = xPercent;
            this.yPercent = yPercent;
            this.ID = ID;
        }

        @Override
        public void run() {

            while (nonZeroValue) {
                // Delay between messages
                try {
                    Thread.sleep(20);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }

                joystickCallback.onJoystickMoved(xPercent, yPercent, ID);
            }
        }
    }
}
