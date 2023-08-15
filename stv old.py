import random
import numpy
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

party_ballots = {}
for party in parties:
    party_ballots[party] = []

#for party_name in parties:
#    try:
#        parties[party_name] = int(input(party_name+' votes: '))
#    except:
#        parties[party_name] = 0
#        print('fuck you')

party_weights = {}
other_parties = {}
""" THIS IS THE FAST METHOD I DONT KNOW HOW IT WORKS
for current_party in parties:
    weights = []
    otherParties = []
    for party, lr in dist.items():
        if party != current_party:
            distance = numpy.reciprocal(abs(dist[current_party] - lr)*16)
            weights.append(distance)
    for party in parties:
        if party != current_party:
            otherParties.append(party)
    party_weights[current_party] = weights
    other_parties[current_party] = otherParties
"""

for current_party, ballots_to_make in parties.items():
    weights = []
    for party, lr in dist.items():
        if party != current_party:
            distance = numpy.reciprocal(abs(dist[current_party] - lr)*16)
            weights.append(distance)
    
    otherParties = []
    for party in parties:
        if party != current_party:
            otherParties.append(party)

    for ballot_n in tqdm(range(ballots_to_make)):
        ballot_weights = weights.copy()
        
        ballot = []
        for ballotRange in range(8):
            choice = random.choices(otherParties,weights=ballot_weights)
            ballot_weights[otherParties.index(choice[0])] = 0
            ballot.append(choice[0])

        party_ballots[current_party].append(ballot)


## STV ZONE ##

winningCandidates = []
n=0

eliminated_parties = []

droop = int(( sum(parties.values()) / candNum + 1 ) + 1)

print(party_weights, other_parties)

while len(winningCandidates) < candNum:
    any_selected = False
    for party, votes in parties.items():
        if votes > droop:
            n += 1
            winningCandidates.append(party)
            print(f"{party}: removing {droop} ballots from {votes}")
            parties[party] -= droop #This is going to create a problem - we need to randomly choose ballots from their pool to remove, this isn't how STV is done, but to do it properly would make me want to die.
            print(f"{party} was elected on the {n} count")
            any_selected = True
    if len(parties) == candNum - len(winningCandidates):
        winningCandidates.extend(parties)
        break
    if not any_selected:
        n += 1
        min_party = None
        lowest_vote = 999999999
        for party, votes in parties.items():
            if votes < lowest_vote:
                min_party = party
                lowest_vote = votes
        if min_party == None:
            print("no parties left :-(")
            break
        print(f"{min_party} was eliminated on the {n} count")
        # other_party_list = other_parties[current_party]

        # ballot_weights = party_weights[min_party]
        #for elim_party in eliminated_parties:
        #    ballot_weights[other_party_list.index(elim_party)] = 0
        #choices = random.choices(other_party_list, weights=ballot_weights, k = parties[min_party])
        #for choice in choices:
        #    if choice in parties:
        #        parties[choice] += 1
        #    else:
        #        print(f"fuck {choice}")
        
        for party, weight_list in party_weights.items():
            if party != min_party:
                elim_party_index = other_parties[party].index(min_party)
                del weight_list[elim_party_index]
                del other_parties[party][elim_party_index]

        #eliminated_parties.append(min_party)

        del parties[min_party]
        #transfer votes to 2nd place options
        #then repeat process, until `candNum = len(winningCandidates)`

print(winningCandidates)
