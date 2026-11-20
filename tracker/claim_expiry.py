"""Preview or release quiet volunteer reservations after their published deadline."""

import argparse
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import os
import re
from urllib.parse import quote

from claim_comments import COMMENT_FEED

WINDOW = timedelta(hours=4)
TARGET = r'P\d{4}|M\d{6}'
EXPIRED = 'claim-expired'
BOT = 'github-actions[bot]'
NOTICE = 'Renewable reservation for'
MODES = ('preview', 'notice', 'enforce')


def utcnow():
    return datetime.now(timezone.utc)


def stamp(value):
    return value.replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def parse(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def volunteer(login, repository):
    return login and login.casefold() != repository.split('/')[0].casefold() and not login.endswith('[bot]')


def notice(target, now):
    return (f'{NOTICE} `{target}`. Initial deadline {stamp(now + WINDOW)}. '
            'A progress or blocker comment on this claim renews it for four hours. '
            'To renew several of your claims in one reply, list their issue numbers or task IDs. '
            'Post your Replay submission here to keep the claim open for review.')


class History:
    def __init__(self):
        self.direct = defaultdict(dict)
        self.mentions = {}

    def update(self, comments):
        for comment in comments:
            number = int(comment['issue_url'].rsplit('/', 1)[1])
            self.direct[number][comment['id']] = comment
            user = comment.get('user') or {}
            if user.get('type') != 'User':
                continue
            login = user['login'].casefold()
            when = parse(comment['created_at'])
            # A claimant may renew several reservations on a single thread.
            for match in re.finditer(r'(?<![\w/])#\d+\b|\b(?:' + TARGET + r')\b', comment['body']):
                key = (login, match[0])
                self.mentions[key] = max(when, self.mentions.get(key, when))

    def decision(self, issue, repo, now):
        user = issue.get('user') or {}
        login = user.get('login')
        match = re.fullmatch(r'Claim (' + TARGET + ')', issue['title'])
        labels = {label['name'] for label in issue['labels']}
        if ('pull_request' in issue or issue['state'] != 'open' or not match or 'claim-granted' not in labels
                or user.get('type') != 'User' or not volunteer(login, repo)):
            return None
        number, target = issue['number'], match[1]
        comments = sorted(self.direct[number].values(), key=lambda c: c['id'])
        grant = None
        announced = None
        latest = None
        for c in comments:
            author = (c.get('user') or {}).get('login', '').casefold()
            body = c['body']
            when = parse(c['created_at'])
            if author == login.casefold():
                if body.lstrip('\ufeff \t\r\n').partition('\n')[0].strip().casefold() == 'replay submission':
                    return None
                latest = when
            if author == BOT:
                if body.startswith(('Granted `', 'No grant.')):
                    grant = when if body.startswith(f'Granted `{target}`.') else None
                    announced = None
                if grant and any(line.startswith(f'{NOTICE} `{target}`.') for line in body.splitlines()):
                    announced = when
        if grant is None:
            return None
        login = login.casefold()
        last = max(grant, announced or grant, latest or grant,
                   self.mentions.get((login, f'#{number}'), grant),
                   self.mentions.get((login, target), grant))
        deadline = last + WINDOW
        if not announced:
            return 'notice', deadline
        if now >= deadline:
            return 'expire', deadline
        return None


def sweep(repo, mode, api, pages, clock=utcnow):
    if mode not in MODES:
        raise ValueError(f'Unknown claim expiry mode: {mode}')
    # Include observations arriving during pagination in the pre-write refresh.
    cursor = clock() - timedelta(seconds=1)
    issues = list(pages('/issues?state=open&labels=claim-granted&per_page=100'))
    history = History()
    history.update(pages('/' + COMMENT_FEED))
    label_ready = False
    counts = defaultdict(int)
    for issue in issues:
        decision = history.decision(issue, repo, clock())
        if not decision:
            continue
        action, deadline = decision
        number = issue['number']
        counts[action] += 1
        if mode == 'preview' or (mode == 'notice' and action == 'expire'):
            print(f'#{number}: would {action} (last activity + 4h: {stamp(deadline)})')
            continue
        if action == 'expire' and not label_ready:
            labels = {label['name'] for label in pages('/labels?per_page=100')}
            if EXPIRED not in labels:
                api('/labels', 'POST', {'name': EXPIRED, 'color': 'c5def5',
                                        'description': 'Volunteer reservation expired after its renewal deadline'})
            label_ready = True
        # Refresh repository comments, including grouped replies on closed claims.
        since = quote(stamp(cursor))
        next_cursor = clock() - timedelta(seconds=1)
        history.update(pages(f'/issues/comments?since={since}&sort=updated&direction=asc&per_page=100'))
        cursor = next_cursor
        route = f'/issues/{number}'
        current = api(route)
        if (current['title'] != issue['title'] or current['comments'] != len(history.direct[number])
                or history.decision(current, repo, clock()) != decision):
            continue
        if action == 'notice':
            api(route + '/comments', 'POST', {'body': notice(current['title'].split()[1], clock())})
        else:
            labels = [label['name'] for label in current['labels'] if label['name'] != 'claim-granted']
            # Change the state and the grant together so a retry sees a closed claim.
            api(route, 'PATCH', {'state': 'closed', 'state_reason': 'not_planned',
                                 'labels': sorted(set(labels) | {EXPIRED})})
        print(f'#{number}: {action} applied', flush=True)
    print(f'{mode}: {counts["notice"]} grants need notice, {counts["expire"]} past deadline.')


if __name__ == '__main__':
    from grants import api, pages
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=MODES, default='preview')
    args = parser.parse_args()
    sweep(os.environ['GITHUB_REPOSITORY'], args.mode, api, pages)
