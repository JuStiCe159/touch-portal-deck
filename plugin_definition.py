PLUGIN_INFO = {
    'sdk': 6,
    'version': 1,
    'name': 'Touch Portal Deck',
    'id': 'TouchPortalDeck',
    'plugin_start_cmd': 'python main.py',
    'plugin_start_cmd_mac': 'sh start.sh main',
    'plugin_start_cmd_linux': 'sh start.sh main',
    'categories': [
        {
            'id': 'deck',
            'name': 'Deck Controls',
            'actions': [
                {
                    'id': 'deck_button',
                    'name': 'Deck Button',
                    'prefix': 'deck',
                    'type': 'communicate',
                    'format': 'Button {$buttonNumber$} pressed',
                    'data': [
                        {
                            'id': 'buttonNumber',
                            'type': 'number',
                            'label': 'Button',
                            'default': '1'
                        }
                    ]
                }
            ]
        }
    ]
}
