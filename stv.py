import random
from tqdm import tqdm

candNum = int(input("Number of Electeds:",))

dist = {
    "Fianna Fáil":-0.3,
    "Fine Gael":-1.0,
    "Sinn Féin":2.0,
    "Social Democratic / Labour Party":1.0,
    "Green Party":0.3,
    "Aontú":0.6,
    "Irish Freedom":-2.6,
    "People Before Profit":2.3,
    "Independent / Other":0.0
}

parties = {
    "Fianna Fáil":484320,
    "Fine Gael":455584,
    "Sinn Féin":535595,
    "Social Democratic / Labour Party":158922,
    "Green Party":155700,
    "Aontú":40917,
    "Irish Freedom":18352,
    "People Before Profit":65841,
    "Independent / Other":266353
}

party_ordering = list(parties)
party_ballots = [None for _ in party_ordering]

for current_party, ballots_to_make in parties.items():
    otherParties = [party for party in parties if party != current_party]
    weights = [(1 / (abs(dist[current_party] - dist[party])*16)) for party in otherParties]
    indexes = list(range(len(otherParties)))
    global_indexes = [party_ordering.index(party) for party in otherParties]

    ballot_counts = {}
    
    for first_choice in tqdm(random.choices(indexes, weights=weights, k=ballots_to_make)):
        ballot_weights = weights.copy()
        ballot_weights[first_choice] = 0
        
        ballot = [otherParties[first_choice]]
        ballot_n = global_indexes[first_choice]
        for ballotRange in range(7):
            choice = random.choices(indexes, weights=ballot_weights)[0]
            ballot_weights[choice] = 0
            ballot_n += global_indexes[choice] * (len(party_ordering) ** (ballotRange + 1))
        if ballot_n in ballot_counts:
            ballot_counts[ballot_n] += 1
        else:
            ballot_counts[ballot_n] = 1
    
    party_ballots[party_ordering.index(current_party)] = ballot_counts

## STV ZONE ##

def count_votes():
    global party_ballots
    global party_ordering
    out = { party: 0 for party in party_ordering }
    for party, ballots in enumerate(party_ballots):
        for count in ballots.values():
            out[party_ordering[party]] += count
    return out

winningCandidates = []
n=0

droop = int(( sum(parties.values()) / candNum + 1 ) + 1)

# this is the fraction of votes that cross party lines to their second
# choice, instead of voting for the same party. since there are no specific 
# per-candidate ballots, this is a way to approximate party allegience.
party_crossing_factor = 0.1

while len(winningCandidates) < candNum:
    any_selected = False
    vote_counts = count_votes()

    for party, votes in vote_counts.items():
        if votes > droop:
            n += 1
            winningCandidates.append(party)

            surplus = int((votes - droop) * party_crossing_factor)
            print(f"{party}: removing {surplus} ballots from {votes}")

            party_index = party_ordering.index(party)
            target_ballots = party_ballots[party_index]
            while surplus > 0:
                for ballot, count in target_ballots.items():
                    to_move = min(surplus, count)
                    to = ballot % len(party_ordering)
                    assert to != party_index
                    surplus -= to_move
                    new_ballot = ballot // len(party_ordering)
                    party_ballots[party_index][ballot] -= to_move
                    if new_ballot in party_ballots[to]:
                        party_ballots[to][new_ballot] += to_move
                    else:
                        party_ballots[to][new_ballot] = to_move
            
            print(f"{party} was elected on the {n} count")
            any_selected = True
    if not any_selected:
        n += 1
        min_party = None
        lowest_vote = None
        for party, votes in vote_counts.items():
            if (lowest_vote is None or votes < lowest_vote) and votes > 0:
                min_party = party
                lowest_vote = votes
        if min_party is None:
            print("no parties left :-(")
            break
        print(f"{min_party} was eliminated on the {n} count")
        
        elim_index = party_ordering.index(min_party)
        target_ballots = party_ballots[elim_index]
        for ballot, count in target_ballots.items():
            to = ballot % len(party_ordering)
            assert to != elim_index
            new_ballot = ballot // len(party_ordering)
            if new_ballot in party_ballots[to]:
                party_ballots[to][new_ballot] += count
            else:
                party_ballots[to][new_ballot] = count
        # all ballots moved
        party_ballots[elim_index] = {}

        #transfer votes to 2nd place options
        #then repeat process, until `candNum = len(winningCandidates)`

print(winningCandidates)
