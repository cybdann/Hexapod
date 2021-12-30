package com.example.hexapodcontrol;

import android.content.Context;
import android.os.Build;
import android.util.Log;

import androidx.annotation.RequiresApi;

import org.eclipse.paho.android.service.MqttAndroidClient;
import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttCallbackExtended;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;

import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

public class MQTTModule {
    private String URI;
    private String username;
    private String password = null;
    private MqttAndroidClient client;
    private IMqttToken token;
    private final Map<String, String> topics;

    public MQTTModule(String URI) {
        this.URI = URI;
        this.topics = new HashMap<String, String>();
    }

    public MQTTModule(String URI, String username, String password) {
        this.URI = URI;
        this.username = username;
        this.password = password;
        this.topics = new HashMap<String, String>();
    }

    public void createClient(Context context) {
        /* Generating a client ID and setting up the android MQTT client*/
        String clientId = MqttClient.generateClientId();
        client = new MqttAndroidClient(context.getApplicationContext(), URI, clientId);

        client.setCallback(new MqttCallbackExtended() {
            @Override
            public void connectComplete(boolean reconnect, String serverURI) {

            }

            @Override
            public void connectionLost(Throwable cause) {

            }

            @RequiresApi(api = Build.VERSION_CODES.N)
            @Override
            public void messageArrived(String topic, MqttMessage message) throws Exception {
                Log.d("MQTTModule", "Message arrived: " + message.toString());
                topics.replace(topic, message.toString());

            }

            @Override
            public void deliveryComplete(IMqttDeliveryToken token) {

            }
        });

        MqttConnectOptions mqttConnectOptions = new MqttConnectOptions();
        mqttConnectOptions.setMqttVersion(MqttConnectOptions.MQTT_VERSION_3_1);
        mqttConnectOptions.setAutomaticReconnect(true);
        mqttConnectOptions.setCleanSession(true);

        /* Connecting to the broker */
        try {
            token = client.connect(mqttConnectOptions);
            token.setActionCallback(new IMqttActionListener() {
                @Override
                public void onSuccess(IMqttToken asyncActionToken) {
                    // We are connected
                    System.out.println("Client connected to the broker!");
                }

                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    // Something went wrong e.g. connection timeout or firewall problems
                    System.out.println(exception.toString());

                }
            });
        } catch (MqttException e) {
            e.printStackTrace();
        }
    }

    public void publishMessage(String topic, String payload, int qos, boolean retainMessage) {
        /* Publishing a message to the broker */
        byte[] encodedPayload;
        try {
            encodedPayload = payload.getBytes(StandardCharsets.UTF_8);
            MqttMessage message = new MqttMessage(encodedPayload);
            message.setQos(qos);
            message.setRetained(retainMessage);
            client.publish(topic, message);
        }
        catch(MqttException e) {
            e.printStackTrace();
        }
    }

    public void subscribeToTopic(String[] sub_topics, int qos) {
        /* Subscribing to the broker and receiving a message */
        for(String topic: sub_topics) {
            if(!topics.containsKey(topic)) {
                topics.put(topic, "");
            }
        }


        token.setActionCallback(new IMqttActionListener() {
            @Override
            public void onSuccess(IMqttToken arg0) {
                try {
                    for(String topic: sub_topics) {
                        client.subscribe(topic, qos, null, new IMqttActionListener() {
                            @Override
                            public void onSuccess(IMqttToken asyncActionToken) {
                                Log.d("MQTTModule", "Successfully subscribed to: " + topic);
                            }

                            @Override
                            public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                                Log.d("MQTTModule", "Failed to subscribed to: " + topic);
                            }
                        });
                    }

                } catch (MqttException e) {
                    e.printStackTrace();
                }
            }

            @Override
            public void onFailure(IMqttToken arg0, Throwable arg1) {
                Log.d("MQTTModule", "Failed");
            }
        });
    }

    public MqttAndroidClient getClient() {
        return client;
    }

    public Map<String, String> getTopics() {
        return topics;
    }
    }
