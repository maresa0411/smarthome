import json
from unittest.mock import Mock, patch

import pytest

from smarthome.model.light import Light


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