def extract_sliver_data(sliver):
    return {
        'description': sliver.description,
        'slice': {
            'name': sliver.slice.name,
            'description': sliver.slice.description,
        },
        'group': {
            'id': sliver.slice.group.id,
            'name': sliver.slice.group.name,
            'description': sliver.slice.group.description,
        }
    }
