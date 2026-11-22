"""Integration assessment guides for the twelve chapter bosses."""
BOSSES = {
10: ('Build a text-based character stat calculator', 'Combine input validation, control flow, ranges, and functions.', 'Empty input, negative values, and boundary scores.'),
20: ('Borrowed text analyzer', 'Use owned input, borrowed slices, mutable aggregation, and avoid unnecessary clones.', 'UTF-8 boundaries, empty text, and borrow scopes.'),
30: ('Domain event registry', 'Model records with structs and enums; use Option, match, and collections.', 'Missing identifiers, duplicates, and state transitions.'),
40: ('Fallible import pipeline', 'Parse multiple records, attach line-specific errors, and prevent numeric overflow.', 'Malformed lines, empty input, and overflow.'),
50: ('Generic ranking library', 'Apply generic type parameters, trait bounds, borrowed inputs, and optional results.', 'Empty collections, ties, and alternative comparable types.'),
60: ('Streaming transformation pipeline', 'Compose closures, iterators, filter/map/fold and avoid unnecessary allocation.', 'Empty streams, repeated elements, and ownership behavior.'),
70: ('Workspace configuration validator', 'Design module boundaries, validate workspace member paths, and document the public API.', 'Path traversal, malformed configuration, and portability.'),
80: ('File ingestion pipeline', 'Combine file I/O, buffered reading, parsing, and structured error reporting.', 'Missing files, invalid encodings, and malformed records.'),
90: ('Concurrent worker pool', 'Coordinate threads with channels and shared state; restore deterministic result order.', 'Worker panics, zero jobs, and racing completion order.'),
100: ('Network protocol gateway', 'Handle TCP framing, timeouts, request validation, and cancellation reasoning.', 'Partial reads, invalid requests, and disconnected peers.'),
110: ('Audited unsafe boundary', 'Encapsulate unsafe operations behind safe APIs and document invariants.', 'Null pointers, aliasing, and invalid lifetimes.'),
120: ('Multi-crate record processor', 'Implement parser, typed errors, checked aggregation, CLI, and integration tests.', 'Invalid IDs, malformed records, overflow, and file I/O failures.'),
}

def guide(level: int, lang: str) -> str:
    title, integration, edges = BOSSES[level]
    if lang == 'FR':
        return (f'\n## Défi intégrateur — {title}\n\n'
                f'**Compétences à combiner :** {integration}\n\n'
                f'**Cas limites à discuter :** {edges}\n\n'
                '### Évaluation orale par le maître du jeu\n'
                '1. Justifie les choix de types et les règles d’ownership.\n'
                '2. Décris deux solutions alternatives et leurs compromis.\n'
                '3. Explique comment les tests prouvent les exigences.\n'
                '4. Décris une défaillance possible et son traitement.\n\n'
                '**Note :** le kata automatique ne valide pas à lui seul le défi intégrateur. '
                'Le maître du jeu doit demander une réalisation supplémentaire avant de décerner la maîtrise du chapitre.\n')
    return (f'\n## Integration challenge — {title}\n\n'
            f'**Skills to combine:** {integration}\n\n'
            f'**Edge cases to discuss:** {edges}\n\n'
            '### Game-master review\n'
            '1. Justify type choices and ownership rules.\n'
            '2. Describe two alternative designs and their tradeoffs.\n'
            '3. Explain how the tests demonstrate requirements.\n'
            '4. Describe a possible failure mode and its mitigation.\n\n'
            '**Note:** the automated kata does not independently certify this integration challenge. '
            'The game master must request an additional implementation before awarding chapter mastery.\n')
