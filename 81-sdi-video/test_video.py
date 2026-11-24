import unittest

from video import RENDITIONS, build_dag, choose, master_playlist, media_playlist, play, run, split, trace


class VideoTest(unittest.TestCase):
    def test_split_last_segment_short(self):
        self.assertEqual(split(30), [4.0] * 7 + [2.0])
        self.assertEqual(split(8), [4.0, 4.0])

    def test_dag_counts_and_order(self):
        dag = build_dag(split(30))
        self.assertEqual(len(dag), 30)
        _, order, _ = run(dag, 4)
        pos = {k: i for i, k in enumerate(order)}
        for k, (_, deps) in dag.items():
            for d in deps:
                self.assertLess(pos[d], pos[k], f"{d} before {k}")
        self.assertEqual(order[-1], "master")

    def test_more_workers_never_slower_and_one_worker_is_sum(self):
        dag = build_dag(split(30))
        ends = [run(dag, w)[0] for w in (1, 4, 12, 24)]
        self.assertEqual(ends, sorted(ends, reverse=True))
        end, _, total = run(dag, 1)
        self.assertAlmostEqual(end, total, delta=0.1)

    def test_playlists(self):
        m = master_playlist()
        self.assertEqual(sum(1 for line in m if line.startswith("#EXT-X-STREAM-INF:BANDWIDTH=")), len(RENDITIONS))
        med = media_playlist(split(30), "360p")
        self.assertEqual(med[2], "#EXT-X-TARGETDURATION:4")
        self.assertEqual(med[-1], "#EXT-X-ENDLIST")
        self.assertEqual(sum(1 for line in med if line.startswith("#EXTINF")), 8)

    def test_choose_with_safety_margin(self):
        self.assertEqual(choose(0)[0], "360p")
        self.assertEqual(choose(3700)[0], "360p")     # 3700 × 0.8 = 2960 < 3000
        self.assertEqual(choose(3750)[0], "720p")
        self.assertEqual(choose(7400)[0], "720p")
        self.assertEqual(choose(7500)[0], "1080p")

    def test_abr_waits_less_than_fixed_top(self):
        tr = trace()
        _, abr = play(tr)
        _, fixed = play(tr, fixed=RENDITIONS[-1])
        self.assertLess(abr, fixed)


if __name__ == "__main__":
    unittest.main()
