from domain.venues_model import venues
from domain.cue_tracks_model import cue_tracks, cue_track_groups
from domain.cue_clusters_model import cue_clusters, cue_cluster_rules
from domain.cue_routing_model import cue_routing

GROUPS = ('RHYTHM-A', 'RHYTHM-B', 'RHYTHM-C')

TRACKS = [
    ('CUE-00', 'HALL-A', [0.65, 1.3, 1.95, 2.6, 3.25, 3.9], 0.0),
    ('CUE-01', 'HALL-A', [1.49, 2.94, 4.39, 5.84, 7.29, 8.74, 10.19], 0.02),
    ('CUE-02', 'HALL-A', [2.33, 4.58, 6.83, 9.08, 11.33, 13.58], 0.04),
    ('CUE-03', 'HALL-A', [0.77, 1.42, 2.07, 2.72, 3.37, 4.02, 4.67], 0.06),
    ('CUE-04', 'HALL-A', [1.45, 2.9, 4.35, 5.8, 7.25, 8.7], 0.08),
    ('CUE-05', 'HALL-A', [2.29, 4.54, 6.79, 9.04, 11.29, 13.54, 15.79], 0.0),
    ('CUE-06', 'HALL-A', [0.73, 1.38, 2.03, 2.68, 3.33, 3.98], 0.02),
    ('CUE-07', 'HALL-A', [1.57, 3.02, 4.47, 5.92, 7.37, 8.82, 10.27], 0.04),
    ('CUE-08', 'HALL-A', [2.25, 4.5, 6.75, 9.0, 11.25, 13.5], 0.06),
    ('CUE-09', 'HALL-A', [0.69, 1.34, 1.99, 2.64, 3.29, 3.94, 4.59], 0.08),
    ('CUE-10', 'HALL-A', [1.53, 2.98, 4.43, 5.88, 7.33, 8.78], 0.0),
    ('CUE-11', 'HALL-A', [2.37, 4.62, 6.87, 9.12, 11.37, 13.62, 15.87], 0.02),
    ('CUE-12', 'HALL-A', [0.65, 1.3, 1.95, 2.6, 3.25, 3.9], 0.04),
    ('CUE-13', 'HALL-A', [1.49, 2.94, 4.39, 5.84, 7.29, 8.74, 10.19], 0.06),
    ('CUE-14', 'HALL-A', [2.33, 4.58, 6.83, 9.08, 11.33, 13.58], 0.08),
    # HALL-B witnesses the same three rhythms after its own first-beat offset.
    ('CUE-B06', 'HALL-B', [1.73, 2.38, 3.03, 3.68, 4.33, 4.98], 0.0),
    ('CUE-B07', 'HALL-B', [2.57, 4.02, 5.47, 6.92, 8.37, 9.82, 11.27], 0.0),
    ('CUE-B08', 'HALL-B', [3.25, 5.5, 7.75, 10.0, 12.25, 14.5], 0.0),
]

FIXTURES = [
    (venues, [{'code': 'HALL-A', 'protocol': 'PULSE4', 'channels': 3, 'ready': True},
 {'code': 'HALL-B', 'protocol': 'METER1', 'channels': 2, 'ready': True},
 {'code': 'HALL-C', 'protocol': 'PULSE4', 'channels': 1, 'ready': False}]),
    (cue_tracks, [{'code': code, 'venue': venue, 'timings': timings, 'shift': shift, 'locked': True}
                  for code, venue, timings, shift in TRACKS]),
    (cue_track_groups, [{'track': code, 'group': GROUPS[index % len(GROUPS)]}
                        for index, (code, venue, timings, shift) in enumerate(TRACKS)]),
    (cue_cluster_rules, [{'code': 'ACTIVE', 'rule': 'absolute', 'trial': None}]),
    (cue_clusters, [{'code': 'BEAT-0',
  'track': 'CUE-00',
  'representative': 'CUE-03',
  'distance': 0.3,
  'members': ['CUE-00', 'CUE-03'],
  'token': 'base'}]),
    (cue_routing, [{'code': 'ROUTE-0',
  'cluster': 'BEAT-0',
  'destination': 'HALL-C',
  'route': 'C-1',
  'status': '分路重排'}]),
]
