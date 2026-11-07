"""Final voice map = union of the bot segments from both detectors
(v2: pYIN low band, v3: cepstral comb). Everything else that is vocal = main.

usage: python3 -I merge_voices.py OUT_DIR
"""
import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blocks import BLOCKS, REC


def union(iv):
    iv = sorted(iv)
    outl = []
    for a, b in iv:
        if outl and a <= outl[-1][1] + 0.15:
            outl[-1][1] = max(outl[-1][1], b)
        else:
            outl.append([a, b])
    return [(round(a, 2), round(b, 2)) for a, b in outl]


def union_gap(iv, gap):
    out = []
    for a, b in sorted(iv):
        if out and a - out[-1][1] < gap:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [(round(a, 2), round(b, 2)) for a, b in out]


def subtract(a, b, cuts):
    res = [(a, b)]
    for c0, c1 in cuts:
        nxt = []
        for x0, x1 in res:
            if c1 <= x0 or c0 >= x1:
                nxt.append((x0, x1))
                continue
            if c0 > x0:
                nxt.append((x0, c0))
            if c1 < x1:
                nxt.append((c1, x1))
        res = nxt
    return [(round(x0, 2), round(x1, 2)) for x0, x1 in res if x1 - x0 >= 0.2]


def main():
    out = sys.argv[1]
    v2 = json.load(open(os.path.join(out, 'voice_map_v2.json')))
    v3 = json.load(open(os.path.join(out, 'voice_map_v3.json')))
    bots = union([(a, b) for a, b, l in v2['segments'] + v3['segments'] if l == 'bot'])
    vocal = union([(a, b) for a, b, l in v3['segments'] if l in ('main', 'bot')] + [(a, b) for a, b, l in v2['segments'] if l in ('main', 'bot')])
    mains = []
    for a, b in vocal:
        mains += subtract(a, b, bots)
    segs = sorted([(a, b, 'bot') for a, b in bots] + [(a, b, 'main') for a, b in mains])
    bt = [t for _, t in BLOCKS]
    ends = bt[1:] + [REC[1][1]]
    ends[37] = REC[0][1]
    per_block = []
    for (num, t0), t1 in zip(BLOCKS, ends):
        ov = lambda lab: round(sum(max(0, min(b, t1) - max(a, t0)) for a, b, l in segs if l == lab), 2)
        per_block.append({'block': num, 't0': round(t0, 2), 't1': round(t1, 2), 'bot_s': ov('bot'), 'main_s': ov('main')})
    gaps = [(0, REC[0][0]), (REC[0][1], REC[1][0]), (REC[1][1], 999)]
    res = {
        'bot_seconds': round(sum(b - a for a, b in bots), 1),
        'main_seconds': round(sum(b - a for a, b in mains), 1),
        'bot_lines': bots,
        'bot_entries': union_gap(bots, 0.5),
        'bot_lines_in_unrecorded_video': [s for s in bots if any(ga <= s[0] < gb for ga, gb in gaps)],
        'bot_voice': v3['summary']['bot'], 'main_voice': v3['summary']['main'],
        'segments': segs, 'per_block': per_block,
    }
    json.dump(res, open(os.path.join(out, 'voice_map_final.json'), 'w'), indent=1)
    fmt = lambda t: f'{int(t // 60)}:{t % 60:04.1f}'
    print('bot s', res['bot_seconds'], ' main s', res['main_seconds'], ' fragments', len(bots), ' entries', len(res['bot_entries']))
    print('bot lines:', [(fmt(a), round(b - a, 1)) for a, b in bots])
    print('blocks with bot:', [(p['block'], p['bot_s'], p['main_s']) for p in per_block if p['bot_s'] >= 0.3])


if __name__ == '__main__':
    main()
