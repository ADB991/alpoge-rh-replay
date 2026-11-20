import io
from datetime import datetime, timezone
import unittest
from unittest.mock import patch

import claim_timing
import grants
from test_coordinator import issue, comment


def event(claim, n, time, body, login='github-actions[bot]'):
    return dict(comment(claim, n, body, login), created_at='2026-11-20T' + time + 'Z')


class ClaimTimingTests(unittest.TestCase):
    def test_packet_with_no_update_before_submission(self):
        packet = issue(434, 'P1288', 'claim', 'claim-granted')
        events = [event(packet, 1, '18:20:42', 'Granted `P1288`.'),
                  event(packet, 2, '19:00:00', 'Still running?', 'reviewer'),
                  event(packet, 3, '20:52:55', '\ufeffReplay submission\nreceipt', 'owner'),
                  event(packet, 4, '21:00:00', 'Replay submission\nrevision', 'owner')]
        rows = list(claim_timing.observations([packet], {434: events}, 'coordinator', '2026-11-20T22:00:00Z'))
        self.assertEqual(rows[0][3:], ('submitted', events[0]['created_at'], events[2]['created_at'], 9133, 9133))

    def test_closed_and_open_intervals_and_regrant(self):
        claim = issue(1, 'P0001', 'claim-granted')
        events = [event(claim, 1, '08:00:00', 'Granted `P0001`.'),
                  event(claim, 2, '09:00:00', 'No grant.'),
                  event(claim, 3, '10:00:00', 'Granted `P0001`.'),
                  event(claim, 4, '10:45:00', 'Uploading', 'owner')]
        now = '2026-11-20T12:00:00Z'
        def rows():
            return list(claim_timing.observations([claim], {1: events}, 'coordinator', now))
        self.assertEqual(rows()[0][3:], ('open', events[2]['created_at'], now, 7200, 4500))
        claim.update(state='closed', closed_at='2026-11-20T11:00:00Z')
        self.assertEqual(rows()[0][3:], ('closed_without_submission', events[2]['created_at'], claim['closed_at'], 3600, 2700))
        claim['user']['login'] = 'Coordinator'
        self.assertEqual(rows(), [])

    def test_submission_after_final_read_keeps_reservation_until_review(self):
        packet = issue(10, 'P0001', 'claim', 'claim-granted')
        competing = issue(11, 'M000001', count=0)
        issues = [packet, competing]
        grant = event(packet, 1, '08:00:00', 'Granted `P0001`.')
        evidence = event(packet, 2, '15:00:00', 'Replay submission\nreceipt', 'owner')
        history = [grant]

        def snapshot(repo):
            read = list(history)
            if evidence not in history:
                history.append(evidence)  # Arrives after the observer's final read.
            return issues, {10: read}

        with patch.object(claim_timing, 'claim_snapshot', snapshot), patch.object(claim_timing, 'datetime', wraps=datetime) as clock:
            clock.now.return_value = datetime(2026, 11, 20, 16, tzinfo=timezone.utc)
            before = io.StringIO()
            claim_timing.report('coord/repo', before)
            self.assertIn('\topen\t', before.getvalue())

            def pages(route):
                return issues if route.startswith('/issues?') else history
            writes = []
            with patch.object(grants, 'load', return_value=[dict(id='M000001', packet='P0001', state='open')]):
                grants.reconcile(pages, lambda *args: writes.append(args))
            self.assertEqual(writes[0], ('/issues/11/labels', 'POST', {'labels': ['claim', 'claim-conflict']}))
            self.assertTrue(all(route.startswith('/issues/11/') for route, *_ in writes))
            self.assertEqual(packet['state'], 'open')
            self.assertIn({'name': 'claim-granted'}, packet['labels'])
            after = io.StringIO()
            claim_timing.report('coord/repo', after)
            self.assertIn('\tsubmitted\t', after.getvalue())
