return {
    node_name: '',
    manifest: {
        timers: ['game_tick']
    },
    persist: {},
    config: {},

    visible_0: false,
    
    tick_period: 600,

    snake_length: 3,
    snake_limit: 9,

    snake_nodes: [
        {
            x: 100,
            y: 30
        },
        {
            x: 110,
            y: 30
        },
        {
            x: 120,
            y: 30
        },
    ],

    food_node: {
        x: 60,
        y: 60
    },

    moving_direction: 1,

    handler: function (arg1, arg2) { // function 1
        this.state_machine._(arg1, arg2)
    },
    log: function(object){
        req_data(this.node_name, '"type": "log", "data":' + JSON.stringify(object), 999999, true)
    },

    calculate_game: function(){
        var step_x = 0, step_y = -10
        if(this.moving_direction === 1){
            step_x = 10, step_y = 0
        }else if(this.moving_direction === 2){
            step_x = 0, step_y = 10
        }else if(this.moving_direction === 3){
            step_x = -10, step_y = 0
        }

        var last_node = {
            x: this.snake_nodes[this.snake_length - 1].x,
            y: this.snake_nodes[this.snake_length - 1].y,
        }

        for(var i = this.snake_length - 1; i > 0; i--){
            this.snake_nodes[i].x = this.snake_nodes[i - 1].x
            this.snake_nodes[i].y = this.snake_nodes[i - 1].y
        }

        var head = this.snake_nodes[0]

        head.x += step_x % 240
        head.y += step_y % 240

        if(head.x === this.food_node.x && head.y === this.food_node.y){
            this.snake_nodes.push(last_node)
            this.snake_length++

            this.food_node.x = 40 + Math.floor(Math.random() * 10) * 10
            this.food_node.y = 40 + Math.floor(Math.random() * 10) * 10
        }
    },

    draw_game: function (response) { // function 2
        var layout_info = {
            json_file: 'snake_layout',
            food_x: this.food_node.x,
            food_y: this.food_node.y,
        }

        for(var i = 0; i < this.snake_length; i++){
            var layout_indices = i + 2
            layout_info['x_' + layout_indices] = this.snake_nodes[i].x
            layout_info['y_' + layout_indices] = this.snake_nodes[i].y
            layout_info['visible_' + layout_indices] = true
        }

        response.draw = {
            update_type: 'du4' // gc4 would refresh the whole screen
        }
        response.draw[this.node_name] = {
            layout_function: 'layout_parser_json',
            layout_info: layout_info
        }
    },
    decode_system_state_update_event: function(system_state_update_event){
        if(system_state_update_event.type !== 'system_state_update') return system_state_update_event;

        return {
            type: system_state_update_event.type,
            concerns_this_app: system_state_update_event.de,
            old_state: system_state_update_event.ze,
            new_state: system_state_update_event.le
        }
    },
    'log': function(object){
        req_data(this.node_name, '"type": "log", "data":' + JSON.stringify(object), 999999, true)
    },
    'init': function () { // function 8
        this.state_machine = new state_machine(this,

            function (self, state_machine, event, response) {
                event = self.decode_system_state_update_event(event)
                
                // if (state_machine.n === 'background') {
                if (event.type === 'system_state_update' && event.concerns_this_app === true && event.new_state === 'visible') {
                    state_machine.d('game_main')
                }else if(event.type === 'middle_hold') {
                    response.action = {
                        type: 'go_back',
                        Se: true // delete memory
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
                    case 'game_main': {
                        if (state_phase == 'entry') {
                            return function (self, response) {
                                response.move = {
                                    'h': 0,
                                    'm': 0,
                                    'is_relative': false
                                }
                                self.draw_game(response)
                                start_timer(self.node_name, 'game_tick', self.tick_period)
                            }
                        }
                        if (state_phase == 'during') {
                            return function (self, state_machine, event, response) {
                                var type = event.type
                                if(type === 'timer_expired'){
                                    if(is_this_timer_expired(event, self.node_name, 'game_tick')){
                                        start_timer(self.node_name, 'game_tick', self.tick_period)
                                        self.calculate_game()
                                        self.draw_game(response)
                                    }
                                }else if(type === 'top_press'){
                                    self.moving_direction--
                                    if(self.moving_direction < 0) self.moving_direction = 3
                                }else if(type === 'bottom_press'){
                                    self.moving_direction = ++self.moving_direction % 4
                                }
                            }
                        }
                        if (state_phase == 'exit') {
                            return function (event, response) { // function 14, 20
                                response.action = {
                                    'type': 'go_back',
                                    'Se': true // delete memory
                                }
                                stop_timer(self.node_name, 'game_tick')
                            }
                        }
                        break;
                    }
                }
                return
            }, undefined, 'background')
    }
}
















