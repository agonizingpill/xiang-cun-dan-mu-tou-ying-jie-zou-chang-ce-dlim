from sqlalchemy import select

from core.queueing import submit, result
from core.records import get, insert, need, scan
from domain.cue_tracks_model import cue_tracks, cue_track_groups
from domain.cue_clusters_model import cue_clusters, cue_cluster_rules, cue_rule_trials


ACTIVE = 'ACTIVE'
DEFAULT_RULE = 'absolute'


def active_rule(conn, lock=False):
    query=select(cue_cluster_rules).where(cue_cluster_rules.c.code==ACTIVE)
    if lock:
        query=query.with_for_update()
    row=conn.execute(query).mappings().first()
    return dict(row) if row is not None else {'code':ACTIVE,'rule':DEFAULT_RULE,'trial':None}


def compare_cues(conn, user, data):
    q=get(conn,cue_tracks,data.track)
    ref=[x for x in scan(conn,cue_tracks) if x['locked'] and x['code']!=data.track]
    need(q['locked'] and 8<=len(ref)<=200,'需要已确认素材及足够参考片段')
    return submit(user,{'task':'compare','rule':active_rule(conn)['rule'],
                        'track':q,'references':ref})


def save_cluster(conn, user, data):
    run=result(user,data.token)
    need(run['input'].get('task','compare')=='compare','该计算凭据属于规则验收，不能保存为节奏簇')
    stats=run['result']
    return insert(conn,cue_clusters,code=data.code,track=run['input']['track']['code'],
      representative=stats['representative'],distance=stats['distance'],members=stats['members'],token=data.token)


def trial_material(conn):
    """Witnessed tracks carrying a rhythm-group label, across every venue."""
    labels={row['track']: row['group'] for row in conn.execute(select(cue_track_groups)).mappings()}
    return [{'code':row['code'],'venue':row['venue'],'timings':row['timings'],'group':labels[row['code']]}
            for row in scan(conn,cue_tracks) if row['locked'] and row['code'] in labels]


def run_rule_trial(conn, user, data):
    material=trial_material(conn)
    venues=sorted({row['venue'] for row in material})
    need(len(venues)>=2 and all(sum(x['venue']==v for x in material)>=2 for v in venues),
         '逐场留出至少需要两个场地各两条已标组的见证拍点')
    need(len(material)<=200,'试验素材超出上限，请先缩减见证拍点')
    baseline=active_rule(conn)['rule']
    need(data.candidate!=baseline,'候选规则与现行规则相同')
    return submit(user,{'task':'rule-trial','baseline':baseline,'candidate':data.candidate,
                        'materials':material})


def _activate(conn, rule, trial):
    """One-shot switch: the first passing trial pins the active rule for every venue."""
    current=active_rule(conn,lock=True)
    need(current['trial'] is None,'规则已一次性切换，不能重复发布')
    present=conn.execute(select(cue_cluster_rules.c.code)
                         .where(cue_cluster_rules.c.code==ACTIVE)).first()
    if present is None:
        conn.execute(cue_cluster_rules.insert().values(code=ACTIVE,rule=rule,trial=trial))
    else:
        conn.execute(cue_cluster_rules.update().where(cue_cluster_rules.c.code==ACTIVE)
                     .values(rule=rule,trial=trial))


def _receipt(row, rule):
    return {'code':row['code'],'verdict':row['verdict'],'published':row['published'],
            'regressed':row['result']['regressed'],'rule':rule}


def _serve_retry(conn, data):
    """A retried acceptance with the same credential returns the original decision."""
    by_code=conn.execute(select(cue_rule_trials)
                         .where(cue_rule_trials.c.code==data.code)).mappings().first()
    if by_code is not None:
        need(by_code['token']==data.token,'试验编号已用于另一批素材，请换编号')
        return _receipt(by_code,active_rule(conn)['rule'])
    by_token=conn.execute(select(cue_rule_trials)
                          .where(cue_rule_trials.c.token==data.token)).mappings().first()
    if by_token is not None:
        need(by_token['code']==data.code,'该计算凭据已用于另一条试验，请换编号')
        return _receipt(by_token,active_rule(conn)['rule'])
    return None


def save_rule_trial(conn, user, data):
    replay=_serve_retry(conn,data)
    if replay is not None:
        return replay
    run=result(user,data.token); stats=run['result']
    need(run['input'].get('task')=='rule-trial','该计算凭据不是规则验收任务，请重取任务号')
    current=active_rule(conn,lock=True)
    need(run['input']['baseline']==current['rule'],'规则已在试验受理后切换，请用当前规则重跑')
    passing=stats['verdict']=='passed'
    if passing:
        need(current['trial'] is None,'规则已一次性切换，不能重复发布')
    row={'code':data.code,'token':data.token,'baseline':run['input']['baseline'],
         'candidate':run['input']['candidate'],'verdict':stats['verdict'],'published':passing,
         'material':run['input']['materials'],'result':stats}
    insert(conn,cue_rule_trials,**row)
    if passing:
        _activate(conn,row['candidate'],row['code'])
    return _receipt(row,row['candidate'] if passing else current['rule'])


VERDICT_LABELS = {'passed': '全部场次过关', 'kept': '保留旧版'}


def list_trials(conn):
    rows=[]
    for row in scan(conn,cue_rule_trials):
        stats=row['result']
        venues=stats['venues']
        rows.append({'code':row['code'],'baseline':row['baseline'],'candidate':row['candidate'],
                     'verdict':row['verdict'],'verdict_label':VERDICT_LABELS.get(row['verdict'],row['verdict']),
                     'published':row['published'],'regressed':stats['regressed'],
                     'mismatch':' · '.join(
                         f"{venue} {stats['stats'][row['baseline']][venue]['mismatch']}"
                         f"→{stats['stats'][row['candidate']][venue]['mismatch']}"
                         for venue in venues)})
    return rows
