# Documentation

## overview
- [How to use the SDK](#how-to-use-the-sdk)
- [How are HR apps structured](#hr-app-structure)
- [Code structure](#code-structure)
- [Callbacks](#callbacks)
- [Events](#events)
- [Api functions](#api-functions)
- [State machine](#state-machine)
- [Layout](#layout)
- [Example](#example)

## How to use the SDK
To use the SDK a few conditions have to be met
- JerryScript v2.1.0 needs to be built with:
```
python3 tools/build.py --jerry-cmdline-snapshot ON
```

- `jerry-snapshot` needs to be in `$PATH`
- `pip3 install crc32c`
- `jq` needs to be installed and executable
- for pushing and installing via Makefile:
    - adb needs to be installed
    - if phone supports adb over wifi, `make connect` can be used after adjusting the Makefile
    - Gadgetbridge needs to be running and connected to the watch. Authentication is not needed.
    - Gadgetbridge needs to have read access to the sd card. Android 11 makes that a bit harder
    
- If the project is an example or derived from one, build/app.json needs to be edited to contain the desired appo id
- then, in the folder where the Makefile lies, `make` can be run. That should
    - `make compile`
    - `make pack`
    - `make push`
    - `make install`
    
    all at once.
- Gadgetbridge should then push the app to the watch. It should be automatically installed.

## HR app structure
each app package is an archive of files.
Those files consist of:
- app executable
- compressed images
- layout files
- single file with app name

The image files are compressed using RLE compression.
Also, each byte in the image file describes one pixel on the screen.
The first two bits describe the blackness, and the third and fourth bit describe alpha.

### app executable
The executable consists of Jerryscript (Javascript framework) compiled
to a function-snapshot.
This is done vie the command-line
```
jerry-snapshot generate -f '' code.js -o code
```
`code` is then executed on the watch and returns an app object.
This object defines the app's meta information and callbacks.
It is mandatory to use JerryScript v2.1.0 as of firmware `DN1.0.2.19r.v7`.

## Code structure
the compiled snapshot need to return an object containing a few fields:
- node_name
    - assigned by master (runtime), equals the apps identifier
- manifest->timers
    - declares the identifiers of all used timers
- init
    - init callback, see callback
- deinit
    - see callbacks
- handler
    - see callbacks
- persist
    - no clue, prolly some persistance manifest
- config
    - puhhh
- additional fields
    - can contain app-scope fields

## Callbacks
### init
- called after applicaiton start
- initializes state machine (in most cases, does not seem necessary)

### deinit
- may be called when app is killed, did not encounter

### handler
- callback receiving system events
- forwards events to state machine (in most cases)
- parameters:
    - event object (further described in events section)
    - response object, used to trigger following actions

## Events
every event is passed to the handler-callback as an object.
The object's type-field contains the event name:
- time_telling_update
    - probably indicates hand movement to show the current time every few seconds
    
- common_update
contains common data such as heart rate info, time info, wear state info. 
For a list of possible fields check the `common` section

    
- timer_expired
    - indicates an expired time, check each timer with `is_this_timer_expired`
    
- user input   ([pos] can be replaces with top/middle/bottom)
    - flick_away
    - double_tap
    - [pos]_press
    - [pos]_short_press_release
    - [pos]_hold
    - [pos]_long_press_release
    
- screen_update_finished

- pending_config_verify
    - indicates the upcoming verification of e.g. config for the backgrounds
    
- node_config_update
    - indicates finished verification
    
- screen_sleep_command_completed
    - what
    
- system_state_update
    - gets broadcastet whenever an app is opened or closed from the launcher
    - contains the following fields:
        - de: boolean indicating if this events has anything to do with receiving app
        - ze: old, exited state
        - le: new, entered state
    - states can have the following values:
        - background: app is running, but in background, e.g. not shown
        - hidden: app is being overlaid by notification or similar
        - visible: app is in foreground
    
## Api functions

### req_data()
sends a request to the phone with an argument string.

parameters:
- node name (can be acquired by this.node_name)
- query string
- timeout (probably)
- some boolean parameter (no clue)

### stop_req_timeout(something, node_name)
stop timer which triggers timeout for requested info using `req_data`

### is_this_query_expired()
probably check data request is expired

### start_timer()
starts a timer with the given parameters:
- node_name (again, this.node_name)
- id (one of the strings declared in the manifest)
- timeout (timer duration in milliseconds)

### stop_timer()
parameters:
- node_name
- timer id (as defined in manifest)

### parseInt(arg)
dunno, might not even be a function

### save_node_persist(node_name)
Each application is an Object.
For persistence to work, the object needs to have a persist field.
[Here](https://github.com/dakhnod/Fossil-HR-Timer/blob/3e031eaa5c85a8bab91bbc02515f50f74b95185a/app.js#L7) is an example.
When calling ```save_node_persist(node_name)```, the OS reads the objects persist.data contents, that contain the fields to be persisted.
Let's say our application looks like this:
```
return {
    node_name: '',
    persist: {
        version: 1,
        data: ['distance', 'names']
    },
    distance: 0.7,
    names: [
        'Daniel',
        'James'
    ],
    ...
}
```
When we then call ```save_node_persist(self.node_name)```, the OS reads the value of distance and names, and stores them.
Next time our application is started and the OS finds those values stored it will assign them in out application.
My [timer](https://github.com/dakhnod/Fossil-HR-Timer/blob/master/app.js) app is a working example of this.

### localization_snprintf()
translates the input according to the installed translation file.
Very similar to snprintf in c.

parameters:
- format string
- parameters

### enable_time_telling()
dunno what this enables, but returns an object containing the hand angles for displaying the time

### disable_time_telling()
disables something

### get_common()
get common data, content unknown yet
also, seems undefined in my test cases.

To access common data, just use the global `common`-object.
```
common['hour']
```
Should contain these fields:
- R
- settings
- unit_setting
- daily_goal
- firmware_version
- serial_number
- default_theme
- hand_hour
- hand_minute
- battery_soc
- battery_voltage
- charge_status
- date
- day
- month
- year
- offset_unix_time_change
- active_minutes
- total_sleep
- step_increase
- time_zone_local
- hour
- minute
- bluetooth_status
- app_status
- chance_of_rain
- hr_bpm
- step_count
- calories
- distance
- weatherInfo
- music_playback_state
- device_offwrist
- ringMyPhone
- pending_config_verify_result
- notification_reply_mask
- hr_bpm_resting
- hr_bpm_peak

### now()
returns the current time in milliseconds.

### is_this_timer_expired(event, node_name, timer_name)
check if a timer is expired based on a `timer_expired`-event.

### move hands
the response abstraction layer can be used for this.
Just call `response = wrap_response(response)`, on the response object, then you can use
`response.move_hands(angle_hour, angle_minute, relative)`.
Also, to move the watch hands the reponse object passed to `handler` needs to be used.
```
response.move = {
    'h': angle,
    'm': angle,
    'is_relative': false
}
```

### draw to screen
the response abstraction layer can be used for this.
Just call `response = wrap_response(response)`, on the response object, then you can use
`response.draw_screen(node_name, full_refresh, layout_info)`.
Also, to draw to the screen a layout system is used. I am unsure whether there is raw access to the screen.
Once again, the response object is used.
```
response.draw = {}
response.draw[this.node_name] = {
    'layout_function': 'layout_parser_json',
    'layout_info': {
        'json_file': 'layout_file',
        'var1': 'bla'
    }
}
```
the keys in `layout_info` (besides json_file) correspond to placeholders set in the layout.

### send generic event

the response abstraction layer can be used for this.
Just call `response = wrap_response(response)`, on the response object, then you can use
`response.draw_screen(node_name, full_refresh, layout_info)`.
For instance, 
```
response.send_user_class_event('double_tap')
``` 
or
```
response.send_generic_event({
    type: 'double_tap',
    class: 'user'
})
```
would light up the screen for a few seconds.

To send a generic event without the layer, set the response.i to an array containing the events
```
response.i = [
    {
        // this will trigger screen illumination for a few secs
        'type': 'double_tap',
        'class': 'user'
    },
    {
        // this will move the hands 360° when showing the time
        'type': 'flick_away',
        'class': 'user'
    }
]
```

### play a notification
to play a notification, the proper event needs to be fired
```
response.i = [
            {
                'type': 'urgent_notification',
                'info': {
                    'title': localization_snprintf('%s', 'Brr Brr'),
                    'app_name': this.package_name,
                    'icon_name': 'icTimer',
                    'Re': 60, // timeout in secs for notification
                    'vibe': {
                        'type': 'timer',
                        'Te': 1500,
                        'Ie': 6000
                    },
                    'exit_event': {
                        'type': 'timer_dismiss'
                    },
                    'actions': [
                        {
                            'Ke': localization_snprintf('%s', 'Dismiss'),
                            'event': {
                                'type': 'timer_dismiss',
                                'param1': 'value1'
                            }
                        },
                        {
                            'Ke': localization_snprintf('%s', 'Repeat'),
                            'event': {
                                'type': 'timer_restart',
                                'param1': 'value1',
                                'param2': 'value2'
                            }
                        }
                    ]
                }
            }
        ]
```
If a menu option within the notification with an event defined is selected, that event and the parameters will be fired.

## State machine
the state machine (state_machine class) provides an api to switch to different states.
## Constructor
params:
- self object
    - object passed to all callbacks, mostly `this` is used
    
- global event handler
    - AFAIK gets called when function `_` of the state machine gets called, which mostly only happens in the `handle`-function
    - is responsible for toggling the state_machine states by calling `state_machine_object.d('new_state')`
    
- state specific event handler
    - on every state change, this function is first called lie this 
        - `callback(old_state, 'exit')`
        - `callback(new_state, 'entry')`
    - also each state can define an event handler thats gets called like this, but only when this state is active
      
      `handler(self_object, state_machine_object, event_object, response_object)`


## Layout

layouts are build hirachically using a JSON definition in a file.
Each node has an id a type, a position, dimensions and a parent container id (besides node 0).

These are some (probably) common fields:
- id
- parent_id
- type
- dimension
    - type
        - no clue, mostly set to "rigid"
    - width
    - height
- placement
    - type
        - whatever, set to "absolute"
    - left
        - space to lef
    - top
        - space to top
- visible
- inversion
    - no clue, someone help me out pls

Here are the so far known types:
- wapp_template
    - no clue that that means, results in a banner. Mostly used as the root node
    - special fields
        - header_icon
            - icon on top of the screen (mostly used as home icon)
            - filename of the file containing the image
        - is_header_selected
            - defines if the header icon is selected
        - title_string
            - dunno what to say about that
    
- option_menu
    - options
        - array of options, set in code in layout_info
    - option_selected
        - number of the selected option
    - is_translate
        - wtf
- container
    - direction
        - 0 = horizontal
        - 1 = vertical
    - main_alignment
        - vertical alignment
        - 0 = align top
        - 1 = align center
        - 2 = align bottom
    - cross_alignment
        - horizontal alignment
        - 0 = align left
        - 1 = align center
        - 2 = align right
- text
    - text
        - this field contains the text displayed
    - ppem
        - the text size in points per m, whatever that means
    - ascent
        - what
    - descent
        - what
    - color
        - a value between 0 and 3, white and black
- text_page
    - text
        - the text displayed
    - line_width
        - an array with three values, probably the width of each text line
    - page_index
        - what
    - ppem
        - text size
    - ascent
        - what
    - descent
        - what
    - justify
        - what
- image
    - image_name
        - the filename of the image to display
    - draw_mode
        - no idea what that means
- solid
    - color
        - well, the color of the solid block, between 0 and 3
- content_table
    - contents
        - contains object with the entries, in this form:
            - icon
                - the icon of the entry
            - text_low
                - the label of the entry

## Example
Examples can be found in the examples folder. Too learn about running examples theck the `How to use the SDK` section.
### simple-menu
this example show a basic menu with a few options and handles button events to scroll through the menu.
