return {
    node_name: '',
    manifest: {
        timers: ['exit', 'second']
    },
    persist: {},
    config: {},
    selected_option: 0,

    handler: function (arg1, arg2) { // function 1
        this.state_machine._(arg1, arg2)
    },
    log: function (object) {
        req_data(this.node_name, '"type": "log", "data":' + JSON.stringify(object), 999999, true)
    },
    header_text: 'Test Menu',
    options: [
        'Option 1',
        'Option 2',
        'Option 3',
    ],
    draw_menu: function (response) { // function 2
        response.draw_screen(
            this.node_name,
            true,
            {
                json_file: 'menu_layout',
                is_header_selected: this.selected_option == -1,
                selected_option: this.selected_option,
                header: localization_snprintf('%s', this.header_text),
                options: this.options
            }
        )
    },
    decode_system_state_update_event: function (system_state_update_event) {
        if (system_state_update_event.type !== 'system_state_update') return system_state_update_event;

        return {
            type: system_state_update_event.type,
            concerns_this_app: system_state_update_event.de,
            old_state: system_state_update_event.ze,
            new_state: system_state_update_event.le
        }
    },
    wrap_response: function (response) {
        response.move_hands = function (degrees_hour, degrees_minute, relative) {
            response.move = {
                h: degrees_hour,
                m: degrees_minute,
                is_relative: relative
            }
        }
        response.go_back = function (kill_app) {
            response.action = {
                type: 'go_back',
                Se: kill_app
            }
        }
        response.go_home = function (kill_app) {
            response.action = {
                type: 'go_home',
                Se: kill_app
            }
        }
        response.draw_screen = function (node_name, full_update, layout_info) {
            response.draw = {
                update_type: full_update ? 'du4' : 'gu4'
            }
            response.draw[node_name] = {
                layout_function: 'layout_parser_json',
                layout_info: layout_info
            }
        }
        response.send_user_class_event = function (event_type) {
            response.send_generic_event({
                type: event_type,
                class: 'user'
            })
        }
        response.send_generic_event = function (event_object) {
            if(response.i == undefined) response.i = []
            response.i.push(event_object)
        }
        return response
    },
    log: function (object) {
        req_data(this.node_name, '"type": "log", "data":' + JSON.stringify(object), 999999, true)
    },
    handle_global_event: function (self, state_machine, event, response) {
        self.log("event type: " + event.type)
        self.log(event)
        event = self.decode_system_state_update_event(event)
        response = self.wrap_response

        if (event.type === 'system_state_update' && event.concerns_this_app === true && event.new_state === 'visible') {
            state_machine.d('menu')
        } else if (event.type === 'middle_hold') {
            response.go_back(true)
        }
    },
    handle_state_specific_event: function (state, state_phase) {
        switch (state) {
            case 'background': {
                if (state_phase == 'during') {
                    return function (self, state_machine, event, response) {

                    }
                }
                break;
            }
            case 'menu': {
                if (state_phase == 'entry') {
                    return function (self, response) {
                        response = self.wrap_response(response)
                        response.move_hands(270, 90, false)
                        self.draw_menu(response)
                    }
                }
                if (state_phase == 'during') {
                    return function (self, state_machine, event, response) {
                        response = self.wrap_response(response)
                        if (event.type === 'middle_short_press_release') {
                            if (self.selected_option === -1) {
                                response.go_home(true)
                                return
                            } else {
                                self.header_text = "selected " + self.options[self.selected_option];
                                self.draw_menu(response)
                                response.send_user_class_event('double_tap')
                            }
                        } else if (event.type === 'top_short_press_release') {
                            if (self.selected_option > -1) {
                                self.selected_option--
                                self.draw_menu(response)
                            }
                        } else if (event.type === 'bottom_short_press_release') {
                            if (self.selected_option < 2) {
                                self.selected_option++
                                self.draw_menu(response)
                            }
                        }
                    }
                }
                if (state_phase == 'exit') {
                    return function (arg, arg2) { // function 14, 20

                    }
                }
                break;
            }
        }
        return
    },
    init: function () { // function 8
        this.state_machine = new state_machine(
            this,
            this.handle_global_event,
            this.handle_state_specific_event,
            undefined,
            'background'
        )
    }
}
















