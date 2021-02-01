return {
    'node_name': '',
    'manifest': {
        'timers': ['exit', 'second']
    },
    'persist': {},
    'config': {},
    'selected_option': 0,

    'handler': function (arg1, arg2) { // function 1
        this.state_machine._(arg1, arg2)
    },
    'log': function(object){
        req_data(this.node_name, '"type": "log", "data":' + JSON.stringify(object), 999999, true)
    },
    'header_text' : 'Test Menu',
    'options': [
        'Option 1',
        'Option 2',
        'Option 3',
    ],
    'draw_menu': function (response) { // function 2
        response.draw = {
            'update_type': 'du4' // gc4 would refresh the whole screen
        }
        response.draw[this.node_name] = {
            'layout_function': 'layout_parser_json',
            'layout_info': {
                'json_file': 'menu_layout',
                'is_header_selected': this.selected_option == -1,
                'selected_option': this.selected_option,
                'header': localization_snprintf('%s', this.header_text),
                'options': this.options
            }
        }
    },
    'decode_system_state_update_event': function(system_state_update_event){
        if(system_state_update_event.type !== 'system_state_update') return system_state_update_event;

        return {
            'type': system_state_update_event.type,
            'concerns_this_app': system_state_update_event.de,
            'old_state': system_state_update_event.ze,
            'new_state': system_state_update_event.le
        }
    },
    'log': function(object){
        req_data(this.node_name, '"type": "log", "data":' + JSON.stringify(object), 999999, true)
    },
    'init': function () { // function 8
        this.state_machine = new state_machine(this,

            function (self, state_machine, event, response) {
                self.log("event type: " + event.type)
                self.log(event)
                event = self.decode_system_state_update_event(event)
                
                // if (state_machine.n === 'background') {
                if (event.type === 'system_state_update' && event.concerns_this_app === true && event.new_state === 'visible') {
                    state_machine.d('menu')
                }else if(event.type === 'middle_hold') {
                    response.action = {
                        'type': 'go_back',
                        'Se': false // delete memory
                    }
                }
            },

            function (state, state_phase) {
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
                                response.move = {
                                    'h': 270,
                                    'm': 90,
                                    'is_relative': false
                                }
                                self.draw_menu(response)
                            }
                        }
                        if (state_phase == 'during') {
                            return function (self, state_machine, event, response) {
                                if (event.type === 'middle_short_press_release') {
                                    if (self.selected_option === -1) {
                                        response.action = {
                                            'type': 'go_home',
                                            'Se': false // delete memory
                                        }
                                        return
                                    }else{
                                        self.header_text = "selected " + self.options[self.selected_option];
                                        self.draw_menu(response)
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
            }, undefined, 'background')
    }
}
















