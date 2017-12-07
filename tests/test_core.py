import unittest

from pypinfo import core


class TestCore(unittest.TestCase):

    def test_tabulate(self):
        # Arrange
        self.maxDiff = None
        rows = [
             ['python_version', 'percent', 'download_count'],
             ['2.7', '51.7%', '342250'],
             ['3.6', '21.1%', '139745'],
             ['3.5', '17.2%', '114254'],
             ['3.4', '7.6%', '50584'],
             ['3.3', '1.0%', '6666'],
             ['3.7', '0.7%', '4516'],
             ['2.6', '0.7%', '4451'],
             ['3.2', '0.0%', '138'],
             ['None', '0.0%', '13']
        ]

        # Act
        tabulated = core.tabulate(rows)
        print(tabulated)

        # Assert
        expected = """\
| python_version | percent | download_count |
| -------------- | ------: | -------------: |
| 2.7            |   51.7% |        342,250 |
| 3.6            |   21.1% |        139,745 |
| 3.5            |   17.2% |        114,254 |
| 3.4            |    7.6% |         50,584 |
| 3.3            |    1.0% |          6,666 |
| 3.7            |    0.7% |          4,516 |
| 2.6            |    0.7% |          4,451 |
| 3.2            |    0.0% |            138 |
| None           |    0.0% |             13 |
"""
        self.assertEqual(tabulated, expected)


if __name__ == '__main__':
    unittest.main()
