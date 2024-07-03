from unittest import TestCase

from extents import Component, interval


class TestIntervalDifference(TestCase):
    def test_difference(self):
        a = interval[0, 10]
        b = interval((2, 3))
        d = a.difference(b)
        self.assertEqual(list(d), [Component(0, 2), Component(3, 10)])


class TestIntervalsRegression(TestCase):
    def test_union_all(self):
        a = interval[7, 10]
        b = interval[0, 3]
        c = ~a | ~b
        self.assertEqual(len(c), 1)

    def test_union_all_rev(self):
        a = interval[0, 3]
        b = interval[7, 10]
        c = ~a | ~b
        self.assertEqual(len(c), 1)

    def test_intersection_none(self):
        a = interval[7, 10]
        b = interval[0, 3]
        c = a & b
        self.assertEqual(len(c), 0)

    def test_intersection_none_rev(self):
        a = interval[0, 3]
        b = interval[7, 10]
        c = a & b
        self.assertEqual(len(c), 0)


class TestIntervalsDocumentationUsage(TestCase):
    def test_construction1(self):
        k = interval([0, 1], [2, 3], [10, 15])
        self.assertEqual(list(k), [Component(0, 1), Component(2, 3), Component(10, 15)])

    def test_construction2(self):
        k = interval[1, 2]
        self.assertEqual(list(k), [Component(1, 2)])

    def test_construction3(self):
        k = interval(1, 2)
        self.assertEqual(list(k), [Component(1, 1), Component(2, 2)])

    def test_construction4(self):
        k = interval(1), interval[1]
        self.assertEqual([list(x) for x in k], [[Component(1, 1)], [Component(1, 1)]])
        self.assertEqual(k[0], k[1])

    def test_construction5(self):
        self.assertEqual(list(interval()), [])

    def test_addition(self):
        pass

    def test_subtraction(self):
        pass

    def test_multiply(self):
        pass

    def test_division(self):
        pass

    def test_intersection(self):
        k = interval[1, 4] & interval[2, 5]
        self.assertEqual(k, interval[2, 4])

    def test_union1(self):
        k = interval[1, 4] | interval[2, 5]
        self.assertEqual(k, interval[1, 5])

    def test_union2(self):
        k = interval[1, 2] | interval[4, 5]
        self.assertEqual(k, interval([1, 2], [4, 5]))

    def test_power(self):
        pass

    def test_abs(self):
        pass

    def test_cast_div(self):
        pass

    def test_inspection(self):
        self.assertTrue(0 in interval[-1, 1])
        self.assertFalse(0 in interval[1, 2])
        self.assertTrue(interval[1, 2] in interval[0, 3])
        self.assertFalse(interval[1, 2] in interval[1.5, 3])

    def test_len(self):
        self.assertEqual(len(interval()), 0)
        self.assertEqual(len(interval[1, 2]), 1)
        self.assertEqual(len(interval(1, 2)), 2)

    def test_iter(self):
        k = [x for x in interval([1, 2], 3)]
        self.assertEqual(k, [Component(1, 2), Component(3, 3)])

    def test_component(self):
        x = interval([1, 2], 3)
        self.assertIsInstance(x[0], Component)
        self.assertEqual(x[0].inf, 1)
        self.assertEqual(x[1].sup, 3)

    def test_components(self):
        k = [x for x in interval([1, 2], 3).components]
        self.assertEqual(k, [interval[1, 2], interval[3]])

    def test_extrema(self):
        k = interval([1, 2], 3)
        self.assertEqual(k.extrema, interval(1, 2, 3))

    def test_midpoint(self):
        k = interval([1, 2], 3)
        self.assertEqual(k.midpoint, interval(1.5, 3))

    def test_invert(self):
        k = interval((0, 100))
        forbidden = interval((1, 2), (1, 40), (2.01, 8), (6, 10), (50, 60))
        # print(k)
        # print(forbidden)
        # print(~forbidden & k)
        sub = ~forbidden & k
        # print([(c[0].inf, c[0].sup) for c in sub.components])
        self.assertEqual([(c[0].inf, c[0].sup) for c in sub.components], [(0, 1), (40, 50), (60, 100)])


class TestIntervalsApiDocumentation(TestCase):
    def test_interval_init(self):
        self.assertEqual(
            list(interval([0, 1], [2, 3], [10, 15])), [Component(0, 1), Component(2, 3), Component(10, 15)]
        )
        self.assertEqual(list(interval(1, [2, 3])), [Component(1, 1), Component(2, 3)])
        self.assertEqual(list(interval[1, 2]), [Component(1, 2)])
        self.assertEqual(list(interval[1]), [Component(1, 1)])

    def test_interval_cast(self):
        self.assertEqual(interval.cast(5), interval[5])

    def test_interval_hull(self):
        self.assertEqual(interval.hull((interval[1, 3], interval[10, 15])), interval[1, 15])
        self.assertEqual(interval.hull([interval(1, 2)]), interval([1, 2]))
