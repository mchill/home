from evdev import InputDevice, categorize, ecodes
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, return_code):
    if return_code != 0:
        print("could not connect, return code:", return_code)


def setup_mqtt_client():
    client = mqtt.Client("Client1")
    client.on_connect=on_connect

    client.connect("host.docker.internal", 1883)
    client.loop_start()

    return client


def read_input(mqtt_client):
    dev = InputDevice("/dev/input/by-id/usb-flirc.tv_flirc_38E36E5950523939352E314AFF061A37-if01-event-kbd")

    with dev.grab_context():
        for event in dev.read_loop():
            if event.type != ecodes.EV_KEY:
                continue

            event = categorize(event)
            if event.keystate != 1:
                continue

            print("key pressed: ", event.keycode)

            result = mqtt_client.publish("remote", event.keycode)
            if result[0] != 0:
                print("Failed to send message to topic")


def main():
    mqtt_client = setup_mqtt_client()
    read_input(mqtt_client)
    client.loop_stop()


if __name__ == "__main__":
    main()
