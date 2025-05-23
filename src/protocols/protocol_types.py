"""
Définition des types de protocoles et leurs caractéristiques.
"""

COMMUNICATION_PROTOCOLS = {
    'http': {
        'security': 'low',
        'encryption': False,
        'authentication': 'none',
        'authorization': 'none',
        'data_sensitivity': 'public'
    },
    'https': {
        'security': 'high',
        'encryption': True,
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'ws': {
        'security': 'low',
        'encryption': False,
        'authentication': 'none',
        'authorization': 'none',
        'data_sensitivity': 'public'
    },
    'wss': {
        'security': 'high',
        'encryption': True,
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'grpc': {
        'security': 'medium',
        'encryption': True,
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'tcp': {
        'security': 'low',
        'encryption': False,
        'authentication': 'none',
        'authorization': 'none',
        'data_sensitivity': 'public'
    },
    'udp': {
        'security': 'low',
        'encryption': False,
        'authentication': 'none',
        'authorization': 'none',
        'data_sensitivity': 'public'
    },
    'mqtt': {
        'security': 'medium',
        'encryption': True,
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'amqp': {
        'security': 'high',
        'encryption': True,
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'kafka': {
        'security': 'high',
        'encryption': True,
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    }
} 