"""
Définition des types de composants et leurs attributs.
"""

COMPONENT_TYPES = {
    'web-application': {
        'styles': ['web', 'browser', 'client', 'frontend', 'ui', 'interface'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'api': {
        'styles': ['api', 'rest', 'graphql', 'endpoint', 'service'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'database': {
        'styles': ['database', 'db', 'sql', 'nosql', 'postgres', 'mysql', 'mongodb', 'oracle'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'confidential'
    },
    'cloud-service': {
        'styles': ['cloud', 'aws', 'azure', 'gcp', 's3', 'lambda', 'function'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'serverless': {
        'styles': ['lambda', 'function', 'serverless', 'faas'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'microservice': {
        'styles': ['service', 'microservice', 'ms', 'backend'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'load-balancer': {
        'styles': ['load-balancer', 'lb', 'haproxy', 'nginx'],
        'authentication': 'none',
        'authorization': 'none',
        'data_sensitivity': 'public'
    },
    'cache': {
        'styles': ['cache', 'redis', 'memcached', 'memory'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'message-queue': {
        'styles': ['queue', 'kafka', 'rabbitmq', 'mq', 'message'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'process': {
        'styles': ['process', 'application', 'app', 'program'],
        'authentication': 'none',
        'authorization': 'none',
        'data_sensitivity': 'public'
    },
    'gateway': {
        'styles': ['gateway', 'api-gateway', 'proxy'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    },
    'cdn': {
        'styles': ['cdn', 'content-delivery', 'edge'],
        'authentication': 'none',
        'authorization': 'none',
        'data_sensitivity': 'public'
    },
    'monitoring': {
        'styles': ['monitoring', 'metrics', 'logging', 'prometheus', 'grafana'],
        'authentication': 'required',
        'authorization': 'required',
        'data_sensitivity': 'internal'
    }
} 