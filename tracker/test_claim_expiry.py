import unittest
from unittest.mock import Mock, patch

from claim_expiry import EXPIRED, History, notice, parse, stamp, sweep
import grants


def hour(n):
    return parse(f'2026-11-20T{n:02}:00:00Z')


def issue(number=10, login='worker'):
    return dict(number=number, title='Claim P0001', state='open', comments=1,
                user=dict(type='User', login=login), labels=[{'name': 'claim-granted'}, {'name': 'claim'}])


def comment(id, when, body, login='github-actions[bot]', number=10):
    return dict(id=id, created_at=stamp(hour(when)), body=body, issue_url=f'https://api.github.com/repos/r/p/issues/{number}',
                user=dict(type='Bot' if login.endswith('[bot]') else 'User', login=login))


GRANTED = 'Granted `P0001`.'
REPO = 'coordinator/repo'


class ClaimExpiryTests(unittest.TestCase):
    def setUp(self):
        self.history = History()
        self.grant = comment(1, 3, GRANTED + '\n\n' + notice('P0001', hour(3)))
        self.history.update([self.grant])
        self.issue = issue()

    def test_grace_starts_with_notice_and_resets_on_regrant(self):
        history = History()
        history.update([comment(1, 1, GRANTED)])
        self.assertEqual(history.decision(self.issue, REPO, hour(9)), ('notice', hour(5)))
        history.update([comment(2, 9, notice('P0001', hour(9)))])
        self.assertIsNone(history.decision(self.issue, REPO, hour(12)))
        self.assertEqual(history.decision(self.issue, REPO, hour(13)), ('expire', hour(13)))
        history.update([comment(3, 13, 'No grant.')])
        self.assertIsNone(history.decision(self.issue, REPO, hour(18)))
        history.update([comment(4, 14, GRANTED)])
        self.assertEqual(history.decision(self.issue, REPO, hour(18)), ('notice', hour(18)))

    def test_grouped_and_direct_renewals_and_nonclaimant_activity(self):
        self.history.update([comment(2, 5, 'My build is blocked', 'Worker'),
                             comment(3, 7, 'Still building #10 and #11', 'worker', 11),
                             comment(4, 8, 'Also running P0001', 'worker', 12),
                             comment(5, 9, 'Status?', 'other'),
                             comment(6, 10, 'working on #100, P00010', 'worker', 12)])
        self.assertIsNone(self.history.decision(self.issue, REPO, hour(11)))
        self.assertEqual(self.history.decision(self.issue, REPO, hour(12)), ('expire', hour(12)))

    def test_protect_submission_owner_managed_and_closed_claims(self):
        for record in [issue(login='Coordinator'), dict(self.issue, state='closed'),
                       dict(self.issue, labels=[]), dict(self.issue, pull_request={}),
                       dict(self.issue, title='Claim M123456')]:
            self.assertIsNone(self.history.decision(record, REPO, hour(12)))
        self.history.update([comment(2, 5, '\ufeffReplay submission\nReceipt', 'worker')])
        self.assertIsNone(self.history.decision(self.issue, REPO, hour(18)))

    def test_sweep_modes_and_recheck(self):
        cases = [
            ('preview', self.grant, [], None),
            ('notice', self.grant, [], None),
            ('enforce', comment(1, 3, GRANTED), [], 'POST'),
            ('enforce', self.grant, [comment(2, 9, 'Still building #10', 'worker', 11)], None),
            ('enforce', self.grant, [comment(2, 9, 'Replay submission\nReceipt', 'worker')], None),
            ('enforce', self.grant, [], 'PATCH'),
        ]
        for mode, grant, updates, write in cases:
            with self.subTest(mode=mode, updates=updates, write=write):
                def pages(route):
                    if route.startswith('/issues?'):
                        return [self.issue]
                    if 'since=' in route:
                        return updates
                    if route.startswith('/labels?'):
                        return [dict(name=EXPIRED)]
                    return [grant]
                refreshed = dict(self.issue, comments=1 + sum(c['issue_url'].endswith('/10') for c in updates))
                api = Mock(return_value=refreshed)
                sweep(REPO, mode, api, pages, lambda: hour(9))
                writes = [c.args for c in api.call_args_list if len(c.args) > 1]
                self.assertEqual([c[1] for c in writes], [write] if write else [])
                if write == 'PATCH':
                    self.assertEqual(writes[0], ('/issues/10', 'PATCH', dict(
                        state='closed', state_reason='not_planned', labels=['claim', EXPIRED])))
                if write == 'POST':
                    self.assertEqual(writes[0], ('/issues/10/comments', 'POST', {'body': notice('P0001', hour(9))}))

    def test_new_and_reopened_grant_publishes_deadline(self):
        opening = dict(issue(), labels=[dict(name=EXPIRED)], comments=0, url='url')
        rows = [dict(id='M000001', packet='P0001', state='open')]
        with patch.dict('os.environ', REPLAY_CLAIM_EXPIRY='notice', GITHUB_REPOSITORY=REPO), \
                patch.object(grants, 'utcnow', return_value=hour(2)), patch.object(grants, 'load', return_value=rows):
            mutate = Mock()
            grants.reconcile(lambda route: [opening] if route.startswith('/issues?') else [], mutate)
            self.assertEqual(mutate.call_args_list[0].args, ('/issues/10/labels/' + EXPIRED, 'DELETE'))
            self.assertIn(notice('P0001', hour(2)), mutate.call_args_list[-1].args[2]['body'])


if __name__ == '__main__':
    unittest.main()
