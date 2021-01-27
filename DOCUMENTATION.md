# Documentation

## overview
- How to use the SDK
- How are HR apps structured
- Code structure
- Callbacks
- Events
- Api functions
- State machine
- Layout
- Example

## How to use the SDK
just don't, yet

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
    - contains common data such as heart rate info, time info, wear state info. Can contain the following fields:
        - hr_bpm
        - hr_bpm_resting
        - hr_bpm_peak
        - music_playback_state
        - day
        - date
        - month
        - year
        - hour
        - minute
        - time_zone_loca
    
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
    - would love to know myself, seems to be broadcastet on apps start
    
## Api functions

### req_data()
sends a request to the phone with an argument string.

parameters:
- node name (can be acquired by this.node_name)
- query string
- timeout (probably)
- some boolean parameter (no clue)

### start_timer()
starts a timer with the given parameters:
- node_name (again, this.node_name)
- id (one of the strings declared in the manifest)
- timeout (timer duration in milliseconds)

### stop_timer()
parameters:
- node_name
- timer id (as defined in manifest)

### localization_snprintf()
translates the input according to the installed translation file.
Very similar to snprintf in c.

parameters:
- format string
- parameters

### now()
returns the current time in milliseconds.

### move hands
to move the watch hands the reponse object passed to `handler` needs to be used.
```
response.move = {
    'h': angle,
    'm': angle,
    'is_relative': false
}
```

### draw to screen
to draw to the screen a layout system is used. I am unsure whether there is raw access to the screen.
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

## Example
// TODO