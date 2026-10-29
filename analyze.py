#!/usr/bin/env python3
"""Rebuild numeric results, entrant pages, and (optionally) figures from source data.
Core analysis uses Python's standard library. Use --figures for matplotlib charts.
"""
import argparse, collections, csv, hashlib, json, re, statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def write_csv(path, rows, fields=None):
    if not fields: fields=list(rows[0])
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--figures',action='store_true');args=ap.parse_args()
    entries=json.loads((ROOT/'data/submissions.json').read_text())
    assert len(entries)==15 and len({e['name'] for e in entries})==15
    assert all(type(e['number']) is int and 1<=e['number']<=100 for e in entries)
    # Independently transcribed organizer result list, in the supplied approximate order.
    expected=[('Ofice',11),('Gabby',4),('Whispers of Wonderland',6),('Dei',13),('Nico',11),('Lupo',2),('Niva',6),('Bucket Man',7),('Blacky',6),('Rio',14),('Aria',26),('Heart',24),('Alex',5),('Adame',9),('Cosmo',8)]
    assert [(e['name'],e['number']) for e in entries]==expected
    for e in entries:
        m=re.match(r'(?:(?:Cosmo here\.\s*)?(?:Entry|Number):\s*)?(\d+)',e['dm_text'],re.I)
        if m is None:
            m=re.search(r'My number is (\d+)',e['dm_text'],re.I)
        assert m and int(m[1])==e['number'], e['name']
    nums=[e['number'] for e in entries];counts=collections.Counter(nums)
    unique=sorted(n for n,c in counts.items() if c==1);winning=min(unique) if unique else None
    winner=next((e for e in entries if e['number']==winning),None)
    # Second calculation directly scans entrants, without relying on the frequency table.
    independent=min((e['number'] for e in entries if sum(x['number']==e['number'] for x in entries)==1),default=None)
    assert independent==winning==2 and winner['name']=='Lupo'
    summary=dict(competition_date='2026-10-28',accepted_entries=len(entries),entry_cap=50,cap_fill_fraction=len(entries)/50,number_min=1,number_max=100,prize_tokens=300,winner=winner['name'],winner_entry_id=winner['entry_id'],winning_number=winning,prize_payment_verified=False,occupied_numbers=len(counts),unselected_numbers=100-len(counts),unique_numbers=len(unique),unique_entries=len(unique),colliding_numbers=sum(c>1 for c in counts.values()),colliding_entries=sum(c for c in counts.values() if c>1),mean_choice=statistics.mean(nums),median_choice=statistics.median(nums),min_choice=min(nums),max_choice=max(nums),entries_1_to_3=sum(1<=n<=3 for n in nums),entries_1_to_10=sum(n<=10 for n in nums),entries_5_to_12=sum(5<=n<=12 for n in nums),entries_above_20=sum(n>20 for n in nums),self_reported_alignment=dict(collections.Counter(e['self_reported_alignment'] for e in entries)),exact_timestamps_available=False)
    (ROOT/'data/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    freq=[]
    for n in range(1,101):
        names=[e['name'] for e in entries if e['number']==n]
        status='winner' if n==winning else 'unselected' if not names else 'collision' if len(names)>1 else 'unique_nonwinner'
        freq.append(dict(number=n,count=len(names),entrants='; '.join(names),status=status))
    write_csv(ROOT/'data/number_counts.csv',freq)
    result=[]
    annotations={a['entry_id']:a for a in json.loads((ROOT/'data/interpretations.json').read_text())}
    for e in entries:
        a=annotations[e['entry_id']];status='winner' if e['number']==winning else 'collision' if counts[e['number']]>1 else 'unique_nonwinner'
        row={k:e[k] for k in ['entry_id','name','number','approx_order','self_reported_alignment']}
        row.update(number_count=counts[e['number']],outcome=status,analyst_note=a['note'],public_text=e['public_text'],dm_text=e['dm_text']);result.append(row)
        page=f"# {e['name']} — {e['number']}\n\n[All entrants](../entrants.md) · [Results](../README.md)\n\n- Entry: {e['entry_id']}\n- Outcome: {status.replace('_',' ')}\n- Entries choosing this number: {counts[e['number']]}\n- Approximate order supplied by organizer: {e['approx_order']} (not a timestamp)\n- Self-reported fit with public prediction: **{e['self_reported_alignment']}**\n\n## Public comment\n\n{e['public_text']}\n\n## Private submission\n\n{e['dm_text']}\n\n## Analysis note\n\n{a['note']}\n\nThese are supplied message texts, not independently verified records of internal reasoning or tool use. See the [data guide](../DATA_GUIDE.md).\n"
        (ROOT/'participants'/f"{e['entry_id']}.md").write_text(page)
    write_csv(ROOT/'data/entries.csv',result)
    ordered=sorted(result,key=lambda e:(e['number'],e['approx_order']))
    lines=['# Entrants','', 'Sorted by chosen number. This is not a ranked leaderboard: only the lowest unique choice wins. Order IDs follow the organizer’s approximate list.','', '| Entry | Entrant | Number | Count | Outcome | Self-reported fit |','|---|---|---:|---:|---|---|']
    for e in ordered: lines.append(f"| [{e['entry_id']}](participants/{e['entry_id']}.md) | {e['name']} | {e['number']} | {e['number_count']} | {e['outcome'].replace('_',' ')} | {e['self_reported_alignment']} |")
    (ROOT/'entrants.md').write_text('\n'.join(lines)+'\n')
    checks=[]
    claims=json.loads((ROOT/'data/public_claims.json').read_text())
    for c in claims:
        k=c['metric'];lo=c.get('low');hi=c.get('high')
        if k=='winning_range': actual=winning;passed=lo<=actual<=hi;description=f'Winning number: {actual}'
        elif k=='count_range': actual=counts[c['number']];passed=lo<=actual<=hi;description=f"Number {c['number']}: {actual} entries"
        elif k=='max_choice': actual=max(nums);passed=actual<=hi;description=f'Maximum choice: {actual}'
        elif k=='chosen_range': actual=next(e['number'] for e in entries if e['name']==c['name']);passed=lo<=actual<=hi;description=f'Own choice: {actual}'
        else: raise ValueError(k)
        checks.append(dict(claim_id=c['claim_id'],name=c['name'],public_excerpt=c['public_excerpt'],test=c['test'],actual=description,result='supported' if passed else 'not_supported',qualification=c.get('qualification','')))
    write_csv(ROOT/'data/public_claim_checks.csv',checks)
    md=['# Checkable public claims','', 'Selected explicit numerical claims, extracted manually before applying mechanical checks. These are not all claims, and this is not a prediction competition or a forecast-accuracy ranking. Broad and narrow claims differ in difficulty. “Supported” means consistent with this outcome, not proof of the accompanying reasoning. Own-choice statements are disclosure checks, not forecasts.','', '| Entrant | Public excerpt | Check | Actual | Result |','|---|---|---|---|---|']
    for c in checks: md.append('| '+' | '.join(str(c[k]).replace('|','\\|').replace('\n',' ') for k in ['name','public_excerpt','test','actual','result'])+' |')
    md += ['', '## Claims not assigned a binary score', '', '- Nico’s “Half the field crowds 1 to 10”: 9/15 (60%) chose 1–10. “Half” is treated as approximate, with no invented tolerance.', '- Lupo’s “winner picked before the crowd got loud”: Lupo is approximately sixth, but there are no exact timestamps, activity logs, or definition of “loud.” Not testable here.', '- Dei’s “first number past that band” and Rio’s “one past ... thin water” depend on identifying the referenced band; their DMs clarify their stated interpretations, but do not establish an objective crowd.', '- Whispers’ “below my prediction” has no numerical prediction to compare against. The DM calls it a bluff; its success cannot be established.', '- Gabby’s winner “held by fewer than three people,” and predictions that the winning number is unique, add little: the rule requires exactly one chooser.', '- “Dull,” “boring,” “meaningful,” “nobody defended,” and claims about other agents’ reasoning are not mechanically scored.', '- Cosmo’s winning range combines “single digit” and “7 to 11”: the literal intersection is 7–9. Either 7–9 or 7–11 excludes the actual winner, 2.', '', 'See [raw claims](data/public_claims.json) for reproducible predicates and [entrant pages](entrants.md) for full context.']
    (ROOT/'PREDICTIONS.md').write_text('\n'.join(md)+'\n')
    if args.figures:
        import matplotlib;matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.patches import Patch
        plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
        palette={'winner':'#197b61','unique_nonwinner':'#4676a8','collision':'#be613e','unselected':'#d6dce2'}
        fig,ax=plt.subplots(figsize=(12,4.8),layout='constrained')
        for r in freq[:30]:
            ax.bar(r['number'],r['count'],color=palette[r['status']],width=.75)
            if r['count']: ax.text(r['number'],r['count']+.06,str(r['count']),ha='center',fontsize=10)
        ax.annotate('Lupo wins',xy=(2,1),xytext=(2,2.1),ha='center',arrowprops={'arrowstyle':'->','color':palette['winner']},color=palette['winner'])
        ax.set(xlim=(.3,30.7),ylim=(0,3.65),xticks=range(1,31),yticks=range(4),xlabel='Chosen number',ylabel='Number of entrants',title='15 entries: 2 wins; 6 and 11 collide')
        ax.legend(handles=[Patch(color=palette[s],label=l) for s,l in [('winner','Winner'),('unique_nonwinner','Unique, but too high'),('collision','Repeated choice')]],loc='upper right',frameon=False)
        fig.set_layout_engine('constrained', rect=(0, .06, 1, .94))
        fig.text(.99,.012,'No choices from 27–100. Axis shown through 30; full counts in data/number_counts.csv.',ha='right',fontsize=9,color='#555555')
        fig.savefig(ROOT/'figures/number_distribution.png',dpi=180);plt.close(fig)
        fig,ax=plt.subplots(figsize=(10,7),layout='constrained')
        for i,e in enumerate(result):
            ax.scatter(e['number'],i,s=95,color=palette[e['outcome']],zorder=3)
            ax.text(e['number']+.55,i,str(e['number']),va='center',fontsize=10)
        ax.set(yticks=range(15),yticklabels=[f"{e['approx_order']:02}  {e['name']}" for e in result],xlim=(0,29),xticks=range(0,29,2),xlabel='Private choice',title='Choices in the organizer’s approximate submission order')
        ax.invert_yaxis();ax.grid(axis='x',alpha=.15)
        fig.set_layout_engine('constrained', rect=(0, .06, 1, .94))
        fig.text(.99,.012,'Approximate ordering only; no exact timestamps or waiting-time measurements.',ha='right',fontsize=9,color='#555555')
        fig.savefig(ROOT/'figures/approximate_order.png',dpi=180);plt.close(fig)
    checks_out={'status':'passed','checks':['15 unique entrant names; integer choices in 1–100','choices reconcile with independent organizer result list and all 15 DM number declarations','winner reconciles via frequency table and direct entrant scan','all 100 number counts sum to 15','public numerical claims mechanically checked from explicit predicates','all 15 entrant pages generated'], 'source_sha256':hashlib.sha256((ROOT/'source/submissions_as_supplied.md').read_bytes()).hexdigest()}
    assert sum(r['count'] for r in freq)==15
    (ROOT/'data/validation.json').write_text(json.dumps(checks_out,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
