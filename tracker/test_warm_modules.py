import io
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import tasks


class WarmCheckoutTests(unittest.TestCase):
    def test_local_objects_transitive_imports_claims_and_ranking(self):
        def row(task, depth, imports=(), state='open'):
            return dict(id=task, packet='P' + task, module='Pkg.' + task,
                        imports=imports, state=state, depth=depth)

        rows = [row('A', 0, state='assigned'), row('B', 1, ['A']),
                row('Missing', 0), row('Hole', 1, ['Missing']),
                row('Gap', 2, ['Hole']), row('D', 2, ['A', 'B', 'B']),
                row('C', 2, ['B']), row('Unlock', 3, ['C', 'C', 'B']),
                row('Other', 3, ['C', 'Missing']), row('Done', 3, ['D'], 'build-observed'),
                row('Taken', 3, ['D']), row('Assigned', 3, ['D'], 'assigned'),
                row('InClaim', 3, ['D']), row('AlreadyBuilt', 2, ['A', 'B'])]
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / 'lean-toolchain').write_text('leanprover/lean4:v4.33.1')
            obj = project / '.lake/build/lib/lean/Pkg'
            obj.mkdir(parents=True)
            for task in ['A', 'B', 'Hole', 'AlreadyBuilt']:
                (obj / (task + '.olean')).touch()
            (obj / 'Missing.olean.hash').touch()
            output = io.StringIO()
            with patch.object(tasks, 'load', return_value=rows[::-1]), \
                 patch.object(tasks, 'claims', return_value={'Taken', 'PInClaim'}), \
                 patch('sys.argv', ['tasks.py', 'next', '--warm', tmp]), redirect_stdout(output):
                self.assertEqual(tasks.main(), 0)
            self.assertEqual(output.getvalue().splitlines(), [
                'C PC Pkg.C cached direct imports 1 newly ready consumers 1',
                'D PD Pkg.D cached direct imports 2 newly ready consumers 0',
            ])


if __name__ == '__main__':
    unittest.main()
