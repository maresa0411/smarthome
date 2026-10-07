import json
from unittest.mock import Mock, patch

import pytest

from datetime import time, datetime

from smarthome.model.light import Light, START_BRIGHTNESS_DEFAULT, END_BRIGHTNESS_DEFAULT, COLOR_ORANGE


@pytest.fixture
def mqtt_client():
    return Mock()


@pytest.fixture
def light(mqtt_client):
    return Light("test_light", mqtt_client)


# -------------------------------------------------------------------
# Initialization / properties
# -------------------------------------------------------------------

def test_initial_state(light):
    assert light.name == "test_light"
    assert light.topic == "zigbee2mqtt/test_light"
    assert light.state == {}
    assert light._off_timer is None
    assert light._alarm_thread is None


def test_properties_without_state(light):
    assert light.is_on is None
    assert light.brightness is None
    assert light.color_temp is None
    assert light.color is None


def test_properties(light):
    light.state = {
        "state": "ON",
        "brightness": 150,
        "color_temp": 300,
        "color": {
            "x": 0.5,
            "y": 0.4
        }
    }

    assert light.is_on is True
    assert light.brightness == 150
    assert light.color_temp == 300
    assert light.color == {
        "x": 0.5,
        "y": 0.4
    }


def test_is_on_false(light):
    light.state = {"state": "OFF"}

    assert light.is_on is False


# -------------------------------------------------------------------
# request_state
# -------------------------------------------------------------------

def test_request_state(light, mqtt_client):
    light.request_state()

    mqtt_client.publish.assert_called_once_with(
        "zigbee2mqtt/test_light/get",
        json.dumps({
            "state": "",
            "brightness": "",
            "color_temp": "",
            "color": ""
        })
    )


# -------------------------------------------------------------------
# State
# -------------------------------------------------------------------

def test_turn_on(light, mqtt_client):
    light.turn_on()

    mqtt_client.publish.assert_called_once_with(
        "zigbee2mqtt/test_light/set",
        json.dumps({"state": "ON"})
    )


def test_turn_off(light, mqtt_client):
    light.turn_off()

    mqtt_client.publish.assert_called_once_with(
        "zigbee2mqtt/test_light/set",
        json.dumps({"state": "OFF"})
    )


def test_toggle_state(light, mqtt_client):
    light.toggle_state()

    mqtt_client.publish.assert_called_once_with(
        "zigbee2mqtt/test_light/set",
        json.dumps({"state": "TOGGLE"})
    )


# -------------------------------------------------------------------
# Brightness
# -------------------------------------------------------------------

@pytest.mark.parametrize(
    "value",
    [0, 1, 100, 253, 254]
)
def test_set_brightness_valid(light, mqtt_client, value):
    light.set_brightness(value)

    mqtt_client.publish.assert_called_once_with(
        "zigbee2mqtt/test_light/set",
        json.dumps({"brightness": value})
    )


@pytest.mark.parametrize(
    "value",
    [-1, 255, 1000]
)
def test_set_brightness_out_of_range(light, value):
    with pytest.raises(ValueError):
        light.set_brightness(value)


@pytest.mark.parametrize(
    "value",
    ["100", None, [], {}, 1.5]
)
def test_set_brightness_invalid_type(light, value):
    with pytest.raises(TypeError):
        light.set_brightness(value)


# -------------------------------------------------------------------
# Color temperature numeric
# -------------------------------------------------------------------

@pytest.mark.parametrize(
    "value",
    [153, 154, 300, 499, 500]
)
def test_set_color_temp_numeric_valid(
    light,
    mqtt_client,
    value
):
    light.set_color_temp(value)

    mqtt_client.publish.assert_called_once_with(
        "zigbee2mqtt/test_light/set",
        json.dumps({"color_temp": value})
    )


@pytest.mark.parametrize(
    "value",
    [152, 501, -1, 1000]
)
def test_set_color_temp_numeric_invalid(light, value):
    with pytest.raises(ValueError):
        light.set_color_temp(value)


# -------------------------------------------------------------------
# Color temperature enum
# -------------------------------------------------------------------

@pytest.mark.parametrize(
    "value",
    [
        "coolest",
        "cool",
        "neutral",
        "warm",
        "warmest"
    ]
)
def test_set_color_temp_enum_valid(
    light,
    mqtt_client,
    value
):
    light.set_color_temp(value)

    mqtt_client.publish.assert_called_once_with(
        "zigbee2mqtt/test_light/set",
        json.dumps({"color_temp": value})
    )


@pytest.mark.parametrize(
    "value",
    [
        "cold",
        "hot",
        "COOL",
        "",
        "invalid"
    ]
)
def test_set_color_temp_enum_invalid(light, value):
    with pytest.raises(ValueError):
        light.set_color_temp(value)


@pytest.mark.parametrize(
    "value",
    [None, [], {}, (1, 2)]
)
def test_set_color_temp_invalid_type(light, value):
    with pytest.raises(TypeError):
        light.set_color_temp(value)


# -------------------------------------------------------------------
# HEX color
# -------------------------------------------------------------------

@pytest.mark.parametrize(
    "value",
    [
        "#000000",
        "#FFFFFF",
        "#ff0000",
        "#12abEF"
    ]
)
def test_set_hex_color_valid(
    light,
    mqtt_client,
    value
):
    light.set_color(value)

    mqtt_client.publish.assert_called_once_with(
        "zigbee2mqtt/test_light/set",
        json.dumps({
            "color": {
                "hex": value
            }
        })
    )


@pytest.mark.parametrize(
    "value",
    [
        "#123",
        "#12345678",
        "123456",
        ""
    ]
)
def test_set_hex_color_invalid_format(light, value):
    with pytest.raises(ValueError):
        light.set_color(value)


@pytest.mark.parametrize(
    "value",
    [
        "#GGGGGG",
        "#12XX34",
        "#ZZZZZZ"
    ]
)
def test_set_hex_color_invalid_characters(light, value):
    with pytest.raises(ValueError):
        light.set_color(value)


# -------------------------------------------------------------------
# RGB
# -------------------------------------------------------------------

@pytest.mark.parametrize(
    "value",
    [
        (0, 0, 0),
        (255, 255, 255),
        (255, 0, 0),
        (12, 100, 254)
    ]
)
def test_set_rgb_valid(
    light,
    mqtt_client,
    value
):
    light.set_color(value)

    r, g, b = value

    mqtt_client.publish.assert_called_once_with(
        "zigbee2mqtt/test_light/set",
        json.dumps({
            "color": {
                "r": r,
                "g": g,
                "b": b
            }
        })
    )


@pytest.mark.parametrize(
    "value",
    [
        (-1, 0, 0),
        (256, 0, 0),
        (0, -1, 0),
        (0, 256, 0),
        (0, 0, -1),
        (0, 0, 256)
    ]
)
def test_set_rgb_out_of_range(light, value):
    with pytest.raises(ValueError):
        light.set_color(value)


@pytest.mark.parametrize(
    "value",
    [
        ("255", 0, 0),
        (0, "255", 0),
        (0, 0, "255"),
        (1.5, 0, 0)
    ]
)
def test_set_rgb_invalid_type(light, value):
    with pytest.raises(TypeError):
        light.set_color(value)


# -------------------------------------------------------------------
# XY color
# -------------------------------------------------------------------

@pytest.mark.parametrize(
    "value",
    [
        (0.0, 0.0),
        (1.0, 1.0),
        (0.5, 0.4),
        (0.123, 0.987)
    ]
)
def test_set_xy_valid(
    light,
    mqtt_client,
    value
):
    light.set_color(value)

    x, y = value

    mqtt_client.publish.assert_called_once_with(
        "zigbee2mqtt/test_light/set",
        json.dumps({
            "color": {
                "x": x,
                "y": y
            }
        })
    )


@pytest.mark.parametrize(
    "value",
    [
        (-0.1, 0.5),
        (1.1, 0.5),
        (0.5, -0.1),
        (0.5, 1.1)
    ]
)
def test_set_xy_out_of_range(light, value):
    with pytest.raises(ValueError):
        light.set_color(value)


@pytest.mark.parametrize(
    "value",
    [
        ("0.5", 0.5),
        (0.5, "0.5"),
        (None, 0.5),
        (0.5, None)
    ]
)
def test_set_xy_invalid_type(light, value):
    with pytest.raises(TypeError):
        light.set_color(value)


# -------------------------------------------------------------------
# Invalid color representations
# -------------------------------------------------------------------

@pytest.mark.parametrize(
    "value",
    [
        None,
        [],
        {},
        (1,),
        (1, 2, 3, 4)
    ]
)
def test_set_color_invalid_format(light, value):
    with pytest.raises(TypeError):
        light.set_color(value)


# -------------------------------------------------------------------
# Timed off
# -------------------------------------------------------------------

def test_turn_on_with_timed_off(light, mqtt_client):
    timer = Mock()

    with patch(
        "smarthome.model.light.threading.Timer",
        return_value=timer
    ) as timer_class:

        light.turn_on_with_timed_off(10)

    mqtt_client.publish.assert_called_once_with(
        "zigbee2mqtt/test_light/set",
        json.dumps({"state": "ON"})
    )

    timer_class.assert_called_once_with(
        10,
        light.turn_off
    )

    assert timer.daemon is True
    timer.start.assert_called_once()
    assert light._off_timer is timer


@pytest.mark.parametrize(
    "seconds",
    [0, -1, -100]
)
def test_timed_off_invalid_seconds(light, seconds):
    with pytest.raises(ValueError):
        light.turn_on_with_timed_off(seconds)


@pytest.mark.parametrize(
    "seconds",
    ["10", 1.5, None, []]
)
def test_timed_off_invalid_type(light, seconds):
    with pytest.raises(TypeError):
        light.turn_on_with_timed_off(seconds)


def test_timed_off_cancels_existing_timer(light):
    old_timer = Mock()
    new_timer = Mock()

    light._off_timer = old_timer

    with patch(
        "smarthome.model.light.threading.Timer",
        return_value=new_timer
    ):
        light.turn_on_with_timed_off(10)

    old_timer.cancel.assert_called_once()
    new_timer.start.assert_called_once()

    assert light._off_timer is new_timer

# -------------------------------------------------------------------
# Light alarm - validation
# -------------------------------------------------------------------

def test_light_alarm_invalid_start_time(light):
    with pytest.raises(TypeError):
        light.set_light_alarm(
            "07:00",
            30
        )


@pytest.mark.parametrize(
    "duration",
    [0, -1, -10, -0.5]
)
def test_light_alarm_invalid_duration(light, duration):
    with pytest.raises(ValueError):
        light.set_light_alarm(
            time(7, 0),
            duration
        )


@pytest.mark.parametrize(
    "duration",
    ["30", None, [], {}, "1.5"]
)
def test_light_alarm_invalid_duration_type(light, duration):
    with pytest.raises(TypeError):
        light.set_light_alarm(
            time(7, 0),
            duration
        )


@pytest.mark.parametrize(
    "brightness",
    [-1, 255, 1000]
)
def test_light_alarm_invalid_start_brightness(light, brightness):
    with pytest.raises(ValueError):
        light.set_light_alarm(
            time(7, 0),
            30,
            start_brightness=brightness
        )


@pytest.mark.parametrize(
    "brightness",
    ["1", 1.5, None, [], {}]
)
def test_light_alarm_invalid_start_brightness_type(light, brightness):
    with pytest.raises(TypeError):
        light.set_light_alarm(
            time(7, 0),
            30,
            start_brightness=brightness
        )


@pytest.mark.parametrize(
    "brightness",
    [-1, 255, 1000]
)
def test_light_alarm_invalid_end_brightness(light, brightness):
    with pytest.raises(ValueError):
        light.set_light_alarm(
            time(7, 0),
            30,
            end_brightness=brightness
        )


@pytest.mark.parametrize(
    "brightness",
    ["254", 254.0, None, [], {}]
)
def test_light_alarm_invalid_end_brightness_type(light, brightness):
    with pytest.raises(TypeError):
        light.set_light_alarm(
            time(7, 0),
            30,
            end_brightness=brightness
        )


def test_light_alarm_end_brightness_smaller_than_start(light):
    with pytest.raises(ValueError):
        light.set_light_alarm(
            time(7, 0),
            30,
            start_brightness=200,
            end_brightness=100
        )


# -------------------------------------------------------------------
# Light alarm - color validation
# -------------------------------------------------------------------

@pytest.mark.parametrize(
    "color",
    [
        "#000000",
        "#FFFFFF",
        "#ff0000",
        (0, 0, 0),
        (255, 170, 5),
        (0.0, 0.0),
        (0.5, 0.4),
    ]
)
def test_light_alarm_valid_color(light, color):
    with patch(
        "smarthome.model.light.threading.Thread"
    ) as thread_class:

        light.set_light_alarm(
            time(7, 0),
            30,
            color=color
        )

        thread_class.assert_called_once()


@pytest.mark.parametrize(
    "color",
    [
        "#123",
        "#12345678",
        "123456",
        "#GGGGGG",
        "#12XX34",
    ]
)
def test_light_alarm_invalid_hex_color(light, color):
    with pytest.raises(ValueError):
        light.set_light_alarm(
            time(7, 0),
            30,
            color=color
        )


@pytest.mark.parametrize(
    "color",
    [
        (-1, 0, 0),
        (256, 0, 0),
        (0, 256, 0),
        (0, 0, 256),
        ("255", 0, 0),
        (255, "170", 5),
        (255, 170, 5.0),
    ]
)
def test_light_alarm_invalid_rgb_color(light, color):
    with pytest.raises((TypeError, ValueError)):
        light.set_light_alarm(
            time(7, 0),
            30,
            color=color
        )


@pytest.mark.parametrize(
    "color",
    [
        (-0.1, 0.5),
        (1.1, 0.5),
        (0.5, -0.1),
        (0.5, 1.1),
        ("0.5", 0.5),
        (0.5, "0.5"),
    ]
)
def test_light_alarm_invalid_xy_color(light, color):
    with pytest.raises((TypeError, ValueError)):
        light.set_light_alarm(
            time(7, 0),
            30,
            color=color
        )


@pytest.mark.parametrize(
    "color",
    [
        None,
        [],
        {},
        (1,),
        (1, 2, 3, 4),
    ]
)
def test_light_alarm_invalid_color_type(light, color):
    with pytest.raises((TypeError, ValueError)):
        light.set_light_alarm(
            time(7, 0),
            30,
            color=color
        )


# -------------------------------------------------------------------
# Light alarm - scheduling
# -------------------------------------------------------------------

def test_light_alarm_creates_thread(light):
    alarm_thread = Mock()

    fixed_now = datetime(2026, 9, 29, 6, 0, 0)

    with patch(
        "smarthome.model.light.datetime"
    ) as datetime_mock, patch(
        "smarthome.model.light.threading.Thread",
        return_value=alarm_thread
    ) as thread_class:

        datetime_mock.now.return_value = fixed_now
        datetime_mock.combine.return_value = datetime(
            2026, 9, 29, 7, 0, 0
        )

        light.set_light_alarm(
            time(7, 0),
            30,
            start_brightness=1,
            end_brightness=254,
            color=(255, 170, 5)
        )

    thread_class.assert_called_once()
    alarm_thread.start.assert_called_once()

    assert light._alarm_thread is alarm_thread


def test_light_alarm_uses_correct_delay(light):
    alarm_thread = Mock()

    fixed_now = datetime(2026, 9, 29, 6, 0, 0)
    alarm_time = datetime(2026, 9, 29, 7, 0, 0)

    with patch(
        "smarthome.model.light.datetime"
    ) as datetime_mock, patch(
        "smarthome.model.light.threading.Thread",
        return_value=alarm_thread
    ) as thread_class:

        datetime_mock.now.return_value = fixed_now
        datetime_mock.combine.return_value = alarm_time

        light.set_light_alarm(
            time(7, 0),
            30
        )

    args = thread_class.call_args.kwargs

    assert args["target"] == light._run_light_alarm
    assert args["args"][0] == 3600
    assert args["args"][1] == 30
    assert args["args"][2] == START_BRIGHTNESS_DEFAULT
    assert args["args"][3] == END_BRIGHTNESS_DEFAULT
    assert args["args"][4] == COLOR_ORANGE


def test_light_alarm_for_tomorrow_if_time_has_passed(light):
    alarm_thread = Mock()

    fixed_now = datetime(2026, 9, 29, 8, 0, 0)
    today_alarm = datetime(2026, 9, 29, 7, 0, 0)

    with patch(
        "smarthome.model.light.datetime"
    ) as datetime_mock, patch(
        "smarthome.model.light.threading.Thread",
        return_value=alarm_thread
    ) as thread_class:

        datetime_mock.now.return_value = fixed_now
        datetime_mock.combine.return_value = today_alarm

        light.set_light_alarm(
            time(7, 0),
            30
        )

    args = thread_class.call_args.kwargs

    # Der Test stellt sicher, dass der Alarm nicht negativ
    # geplant wird.
    assert args["args"][0] > 0


# -------------------------------------------------------------------
# Light alarm - execution
# -------------------------------------------------------------------

def test_light_alarm_starts_light(light):
    light.set_color = Mock()
    light.set_brightness = Mock()
    light.turn_on = Mock()

    # Kein tatsächliches Warten
    light._alarm_stop_event = Mock()
    light._alarm_stop_event.wait.return_value = False

    with patch.object(
        light,
        "_fade_brightness"
    ) as fade_mock:

        light._run_light_alarm(
            delay=0,
            duration=30,
            start_brightness=1,
            end_brightness=254,
            color=(255, 170, 5),
        )

    light.set_color.assert_called_once_with((255, 170, 5))
    light.set_brightness.assert_called_once_with(1)
    light.turn_on.assert_called_once()

    fade_mock.assert_called_once_with(
        duration=30,
        start_brightness=1,
        end_brightness=254,
    )


def test_light_alarm_can_be_cancelled_before_start(light):
    light._alarm_stop_event = Mock()
    light._alarm_stop_event.wait.return_value = True

    light.set_color = Mock()
    light.set_brightness = Mock()
    light.turn_on = Mock()

    light._run_light_alarm(
        delay=3600,
        duration=30,
        start_brightness=1,
        end_brightness=254,
        color=(255, 170, 5),
    )

    light.set_color.assert_not_called()
    light.set_brightness.assert_not_called()
    light.turn_on.assert_not_called()


# -------------------------------------------------------------------
# Light alarm - fade
# -------------------------------------------------------------------

def test_fade_brightness(light):
    light.set_brightness = Mock()

    # Sofort zurückkehren, damit der Test nicht wirklich wartet.
    light._alarm_stop_event = Mock()
    light._alarm_stop_event.wait.return_value = False

    light._fade_brightness(
        duration=1,
        start_brightness=1,
        end_brightness=5,
    )

    assert light.set_brightness.call_count == 4

    expected_calls = [
        ((2,),),
        ((3,),),
        ((4,),),
        ((5,),),
    ]

    assert light.set_brightness.call_args_list == expected_calls


def test_fade_brightness_waits_correct_interval(light):
    light.set_brightness = Mock()

    light._alarm_stop_event = Mock()
    light._alarm_stop_event.wait.return_value = False

    light._fade_brightness(
        duration=1,
        start_brightness=1,
        end_brightness=3,
    )

    # 1 Minute / 2 Helligkeitsstufen = 30 Sekunden
    assert light._alarm_stop_event.wait.call_count == 2

    light._alarm_stop_event.wait.assert_any_call(30)


def test_fade_brightness_does_nothing_if_brightness_is_equal(light):
    light.set_brightness = Mock()

    light._fade_brightness(
        duration=30,
        start_brightness=100,
        end_brightness=100,
    )

    light.set_brightness.assert_not_called()


def test_fade_brightness_can_be_cancelled(light):
    light.set_brightness = Mock()

    light._alarm_stop_event = Mock()

    # Bereits beim ersten Warten abbrechen
    light._alarm_stop_event.wait.return_value = True

    light._fade_brightness(
        duration=30,
        start_brightness=1,
        end_brightness=254,
    )

    light.set_brightness.assert_not_called()


# -------------------------------------------------------------------
# Light alarm - cancellation
# -------------------------------------------------------------------

def test_cancel_light_alarm(light):
    alarm_thread = Mock()

    light._alarm_thread = alarm_thread

    light.cancel_light_alarm()

    assert light._alarm_stop_event.is_set()
    assert light._alarm_thread is None


def test_setting_new_light_alarm_cancels_existing_alarm(light):
    old_thread = Mock()
    new_thread = Mock()

    light._alarm_thread = old_thread

    with patch.object(
        light._alarm_stop_event,
        "set",
        wraps=light._alarm_stop_event.set
    ) as stop_event:

        fixed_now = datetime(2026, 9, 29, 6, 0, 0)
        alarm_time = datetime(2026, 9, 29, 7, 0, 0)

        with patch(
            "smarthome.model.light.datetime"
        ) as datetime_mock, patch(
            "smarthome.model.light.threading.Thread",
            return_value=new_thread
        ):

            datetime_mock.now.return_value = fixed_now
            datetime_mock.combine.return_value = alarm_time

            light.set_light_alarm(
                time(7, 0),
                30
            )

    stop_event.assert_called_once()
    new_thread.start.assert_called_once()
    assert light._alarm_thread is new_thread