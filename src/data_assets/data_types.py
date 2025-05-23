"""
Définition des types de données et leurs sensibilités.
"""

DATA_TYPES = {
    'user': {
        'sensitivity': 'confidential',
        'description': 'Données utilisateur',
        'examples': ['credentials', 'profile', 'personal', 'user', 'account']
    },
    'business': {
        'sensitivity': 'restricted',
        'description': 'Données métier',
        'examples': ['transactions', 'orders', 'invoices', 'payment', 'business', 'financial']
    },
    'system': {
        'sensitivity': 'internal',
        'description': 'Données système',
        'examples': ['logs', 'metrics', 'config', 'system', 'monitoring', 'performance']
    },
    'public': {
        'sensitivity': 'public',
        'description': 'Données publiques',
        'examples': ['content', 'static', 'media', 'public', 'website', 'blog']
    }
} 