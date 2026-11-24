import numpy as np
from sklearn.cluster import AgglomerativeClustering

RULES = ('absolute', 'first-beat')


def normalize(timings, rule):
    if rule == 'absolute':
        return [float(x) for x in timings]
    if rule == 'first-beat':
        return [float(x) - float(timings[0]) for x in timings]
    raise ValueError('未知分簇规则')


def dtw(a,b):
    dist=np.full((len(a)+1,len(b)+1),np.inf)
    dist[0,0]=0
    for i,x in enumerate(a,1):
        for j,y in enumerate(b,1):
            dist[i,j]=abs(x-y)+min(dist[i-1,j],dist[i,j-1],dist[i-1,j-1])
    return float(dist[-1,-1]/(len(a)+len(b)))


def distance_matrix(rows, rule=RULES[0]):
    series=[normalize(row['timings'],rule) for row in rows]
    count=len(series)
    distances=np.zeros((count,count))
    for i in range(count):
        for j in range(i):
            distances[i,j]=distances[j,i]=dtw(series[i],series[j])
    return distances


def _labels(distances):
    count=len(distances)
    return AgglomerativeClustering(n_clusters=min(3,count),metric='precomputed',
                                   linkage='average').fit_predict(distances)


def join_query(distances, positions):
    """Cluster the references plus the query (last position); None when it joins no reference."""
    indices=list(positions)
    labels=_labels(distances[np.ix_(indices,indices)])
    target=labels[-1]
    members=[indices[p] for p in range(len(indices)-1) if labels[p]==target]
    if not members:
        return None
    representative=min(members,key=lambda i:float(sum(distances[i,j] for j in members)))
    return {'members':members,'representative':representative}


def compare_cues(data):
    rule=data.get('rule',RULES[0])
    if rule not in RULES:
        raise ValueError('未知分簇规则')
    rows=data['references']+[data['track']]
    distances=distance_matrix(rows,rule)
    joined=join_query(distances,range(len(rows)))
    if joined is None:
        raise ValueError('当前轨迹独立成簇，需追加场测')
    representative=joined['representative']
    return {'representative':rows[representative]['code'],
            'distance':round(float(distances[representative,-1]),4),
            'members':[rows[i]['code'] for i in joined['members']],
            'reference_count':len(rows)-1,'rule':rule}


def evaluate_trial(materials, baseline=RULES[0], candidate=RULES[1]):
    """Leave one venue out: every venue's tracks become queries, other venues are references.

    Both rules run against the same material snapshot. A query is a mismatch when it joins
    no cluster at all, or when its cluster representative carries a different rhythm group.
    """
    for rule in (baseline,candidate):
        if rule not in RULES:
            raise ValueError('未知分簇规则')
    if baseline == candidate:
        raise ValueError('新旧规则需不同')
    venues=sorted({row['venue'] for row in materials})
    if len(venues)<2:
        raise ValueError('逐场留出至少需要两个场地的见证拍点')
    stats={}
    for rule in (baseline,candidate):
        distances=distance_matrix(materials,rule)
        per_venue={}
        for venue in venues:
            references=[i for i,row in enumerate(materials) if row['venue']!=venue]
            queries=[i for i,row in enumerate(materials) if row['venue']==venue]
            record={'total':len(queries),'mismatch':0,'unclustered':0,'wrong':0,'errors':[]}
            for query in queries:
                joined=join_query(distances,references+[query])
                if joined is None:
                    record['mismatch']+=1
                    record['unclustered']+=1
                    record['errors'].append({'track':materials[query]['code'],'reason':'unclustered'})
                    continue
                representative=materials[joined['representative']]
                if representative['group']!=materials[query]['group']:
                    record['mismatch']+=1
                    record['wrong']+=1
                    record['errors'].append({'track':materials[query]['code'],
                                             'reason':'representative-group',
                                             'representative':representative['code'],
                                             'expected':materials[query]['group'],
                                             'predicted':representative['group']})
            per_venue[venue]=record
        stats[rule]=per_venue
    regressed=[venue for venue in venues
               if stats[candidate][venue]['mismatch']>stats[baseline][venue]['mismatch']]
    return {'venues':venues,'baseline':baseline,'candidate':candidate,'stats':stats,
            'regressed':regressed,'verdict':'kept' if regressed else 'passed'}


def calculate(data):
    task=data.get('task','compare')
    if task == 'rule-trial':
        return evaluate_trial(data['materials'],data['baseline'],data['candidate'])
    if task == 'compare':
        return compare_cues(data)
    raise ValueError('未知计算任务')
