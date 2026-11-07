"""Song map figure: sections, the two voices, loudness, video blocks.

usage: python3 -I songmap.py OUT_DIR OUT_PNG
"""
import sys, os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blocks import BLOCKS, REC

SURF, INK, INK2, MUTED = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8984'
MAIN, BOT = '#2a78d6', '#eb6834'
SEC_FILL, CHORUS_FILL = '#ecebe8', '#d9d6cf'

SECTIONS = [
    (0.0, 17.5, 'Интро\n(говорок)'), (17.5, 33.5, 'Инструментал'), (33.5, 63.5, 'Куплет 1'),
    (63.5, 85.5, 'Пре-припев'), (85.5, 117.5, 'Припев 1'), (117.5, 125.5, 'Отчёт\nбота'),
    (125.5, 145.5, 'Куплет 2'), (145.5, 161.5, 'Пре-припев'), (161.5, 193.5, 'Припев 2'),
    (193.5, 199.5, 'Брейк'), (199.5, 223.5, 'Бридж «инцидент»'), (223.5, 251.5, 'Разгон'),
    (251.5, 291.5, 'Финальный припев + кода'), (291.5, 305.1, 'Аутро\n(говорок)'),
]
CHORUS = {'Припев 1', 'Припев 2', 'Финальный припев + кода'}


def main():
    out, png = sys.argv[1], sys.argv[2]
    vm = json.load(open(os.path.join(out, 'voice_map_final.json')))
    bf = np.load(os.path.join(out, 'bars_features.npz'))
    t_lu, Sst = bf['t_lu'], bf['Sst']
    rows = [(0, 102), (102, 204), (204, 306)]
    prev_label_t, alt = -99, False
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'text.color': INK, 'axes.labelcolor': INK2,
                         'xtick.color': INK2, 'ytick.color': INK2, 'axes.edgecolor': '#cfcdc8'})
    fig = plt.figure(figsize=(16, 11.6), facecolor=SURF)
    fig.text(0.012, 0.975, 'LGTM — карта трека', fontsize=15, weight='bold', va='top')
    fig.text(0.012, 0.947, f"5:05 · 120 BPM, такт 2 с · основной голос ≈ {vm['main_seconds']:.0f} с, "
             f"бот — {len(vm['bot_entries'])} коротких выходов ≈ {vm['bot_seconds']:.0f} с", fontsize=10.5, color=INK2, va='top')
    # legend
    lx = 0.50
    for i, (col, lab) in enumerate([(MAIN, 'основной голос'), (BOT, 'бот (металлический)')]):
        fig.patches.append(Rectangle((lx + i * 0.15, 0.952), 0.016, 0.012, transform=fig.transFigure, color=col))
        fig.text(lx + i * 0.15 + 0.021, 0.958, lab, fontsize=9.5, va='center', color=INK)
    fig.patches.append(Rectangle((lx + 0.30, 0.952), 0.016, 0.012, transform=fig.transFigure, facecolor='none',
                                 edgecolor=MUTED, hatch='////', lw=0))
    fig.text(lx + 0.321, 0.958, 'видео не записано', fontsize=9.5, va='center', color=INK)

    H = 0.25
    for r, (a, b) in enumerate(rows):
        y0 = 0.90 - (r + 1) * 0.28 + 0.03
        ax = fig.add_axes([0.075, y0, 0.91, H])
        ax.set_facecolor(SURF)
        ax.set_xlim(a, b)
        ax.set_ylim(0, 10)
        ax.set_yticks([])
        for s in ('top', 'right', 'left'):
            ax.spines[s].set_visible(False)
        ticks = np.arange(np.ceil(a / 10) * 10, b + 0.1, 10)
        ax.set_xticks(ticks)
        ax.set_xticklabels([f'{int(t // 60)}:{int(t % 60):02d}' for t in ticks], fontsize=8)
        for t in ticks:
            ax.axvline(t, color='#ecebe8', lw=0.6, zorder=0)
        # lane labels
        for yy, lab in ((8.6, 'Разделы'), (6.55, 'Голос'), (5.45, 'Бот'), (3.3, 'Громкость'), (0.9, 'Блоки')):
            fig.text(0.07, y0 + H * yy / 10, lab, ha='right', va='center', fontsize=8.5, color=INK2)
        # sections
        for s0, s1, lab in SECTIONS:
            if s1 <= a or s0 >= b:
                continue
            x0, x1 = max(s0, a), min(s1, b)
            ax.add_patch(Rectangle((x0 + 0.15, 7.6), x1 - x0 - 0.3, 2.0, color=CHORUS_FILL if lab in CHORUS else SEC_FILL, lw=0))
            if x1 - x0 > 5.5:
                ax.text((x0 + x1) / 2, 8.6, lab, ha='center', va='center', fontsize=8.6 if x1 - x0 > 9 else 7.2,
                        weight='bold' if lab in CHORUS else 'normal', color=INK)
        # voices: two lanes
        for s0, s1, lab in vm['segments']:
            if s1 <= a or s0 >= b:
                continue
            x0, x1 = max(s0, a), min(s1, b)
            if lab == 'main':
                ax.add_patch(Rectangle((x0, 6.15), x1 - x0, 0.8, color=MAIN, lw=0))
            elif lab == 'bot':
                ax.add_patch(Rectangle((x0, 5.05), x1 - x0, 0.8, color=BOT, lw=0))
        # loudness, short-term LUFS mapped -26..-12 -> 1.9..4.6
        m = (t_lu >= a) & (t_lu <= b)
        yy = 1.9 + (np.clip(Sst[m], -26, -12) + 26) / 14 * 2.7
        ax.plot(t_lu[m], yy, color=INK2, lw=1.4)
        if r == 0:
            ax.text(a + 0.5, 4.75, '−12 LUFS', fontsize=7, color=MUTED, va='bottom')
            ax.text(a + 0.5, 1.75, '−26', fontsize=7, color=MUTED, va='top')
        # blocks
        for n, t in BLOCKS:
            if a <= t < b:
                alt = (not alt) if t - prev_label_t < 2.6 else False
                prev_label_t = t
                ax.plot([t, t], [0.15, 1.4], color=INK2, lw=0.9)
                ax.text(t + 0.25, 1.1 if not alt else 0.4, str(n), fontsize=7.4, color=INK, va='center')
        # unrecorded video
        for g0, g1 in [(0, REC[0][0]), (REC[0][1], REC[1][0]), (REC[1][1], 305.1)]:
            if g1 <= a or g0 >= b:
                continue
            ax.add_patch(Rectangle((max(g0, a), 0.1), min(g1, b) - max(g0, a), 1.4, facecolor='none', edgecolor=MUTED, hatch='////', lw=0))
    fig.text(0.075, 0.012, 'Разделы — по самоподобию тактов и громкости; голоса — по отделённому вокалу: бот = ровная гребёнка гармоник около 87 Гц (F2). '
             'Номера блоков — из каталога, время ±1 с.', fontsize=8, color=MUTED)
    fig.savefig(png, dpi=100, facecolor=SURF)


if __name__ == '__main__':
    main()
