        import {workspace} from '../workspace.js';
        import {el} from '../dom.js';

        const page = {
  "title": "节奏相近的对场 cue",
  "module": "对场节奏簇",
  "caption": "对场节奏簇",
  "detail": "DTW 比较长短不同的拍点序列，然后按预计算距离做凝聚层次分类。",
  "path": "/cue_clusters",
  "columns": [
    {
      "name": "code",
      "label": "编号"
    },
    {
      "name": "track",
      "label": "输入素材"
    },
    {
      "name": "representative",
      "label": "簇样板"
    },
    {
      "name": "distance",
      "label": "DTW 距离"
    },
    {
      "name": "members",
      "label": "簇内轨迹"
    },
    {
      "name": "token",
      "label": "计算凭据"
    }
  ],
  "layout": "split",
  "view": "grid",
  "extras": [
    {
      "caption": "现行分簇规则",
      "path": "/cue_clusters/rule",
      "columns": [
        {
          "name": "rule",
          "label": "规则"
        },
        {
          "name": "trial",
          "label": "切换验收"
        }
      ],
      "view": "grid"
    },
    {
      "caption": "规则验收记录",
      "path": "/cue_clusters/rule-trials",
      "columns": [
        {
          "name": "code",
          "label": "验收编号"
        },
        {
          "name": "verdict_label",
          "label": "结论"
        },
        {
          "name": "published",
          "label": "已切换"
        },
        {
          "name": "regressed",
          "label": "错配变多的场地"
        },
        {
          "name": "mismatch",
          "label": "逐场错配"
        }
      ],
      "view": "grid"
    }
  ],
  "actions": [
    {
      "name": "compare_cues",
      "label": "计算可迁移节奏簇",
      "path": "/cue_clusters/compare-cues",
      "fields": [
        {
          "name": "track",
          "label": "试投素材",
          "kind": "text",
          "initial": "CUE-FINAL"
        }
      ],
      "help": "返回最近代表 cue 与簇内成员。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已写入"
    },
    {
      "name": "save_cluster",
      "label": "保留对场节奏凭据",
      "path": "/cue_clusters/save-cluster",
      "fields": [
        {
          "name": "code",
          "label": "节奏簇编号",
          "kind": "text",
          "initial": "BEAT-24"
        },
        {
          "name": "token",
          "label": "任务",
          "kind": "token",
          "initial": ""
        }
      ],
      "help": "输出供放映领班查阅的代表节奏。",
      "roles": [
        "reviewer"
      ],
      "success": "已写入"
    },
    {
      "name": "run_rule_trial",
      "label": "逐场留出试跑扣首拍规则",
      "path": "/cue_clusters/run-rule-trial",
      "fields": [
        {
          "name": "candidate",
          "label": "候选规则",
          "kind": "text",
          "initial": "first-beat"
        }
      ],
      "help": "用其他场地的已标组见证拍点做参考，任一场错配变多即保留旧版。",
      "roles": [
        "reviewer"
      ],
      "success": "已写入",
      "summarize": value => (value.verdict === 'passed' ? '全部场次过关，可签认切换' : '保留旧版') +
        (value.regressed && value.regressed.length ? ' · 错配变多：' + value.regressed.join('、') : '')
    },
    {
      "name": "save_rule_trial",
      "label": "签认规则验收",
      "path": "/cue_clusters/save-rule-trial",
      "fields": [
        {
          "name": "code",
          "label": "验收编号",
          "kind": "text",
          "initial": "RULE-24"
        },
        {
          "name": "token",
          "label": "任务",
          "kind": "token",
          "initial": ""
        }
      ],
      "help": "全部场次过关才一次性切换；重试同一任务不会重复发布。",
      "roles": [
        "reviewer"
      ],
      "success": "已写入",
      "summarize": value => (value.published ? '已切换到 ' : '保留 ') + value.rule +
        ' · ' + value.verdict
    }
  ]
};

        export const {title} = page;
        export const key = "cue_clusters";
        export async function render(root, role) {
          await workspace(root, role, page);

        }
