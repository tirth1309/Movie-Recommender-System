from collections import defaultdict
TOP_MOVIES="rashomon+1950,the+apartment+1960,his+girl+friday+1940,the+shawshank+redemption+1994,buena+vista+social+club+1999,princess+mononoke+1997,in+the+mood+for+love+2000,bob+roberts+1992,the+godfather+1972,harry+potter+and+the+deathly+hallows+part+2+2011,witness+for+the+prosecution+1957,my+neighbor+totoro+1988,little+big+man+1970,the+triplets+of+belleville+2003,the+400+blows+1959,the+seventh+seal+1957,castle+in+the+sky+1986,schindlers+list+1993,m+1931,paths+of+glory+1957"
movies = TOP_MOVIES.split(",")
crafted_movies = ['the+fifth+element+1997', 'constantine+2005', 'ratatouille+2007', 'the+hobbit+an+unexpected+journey+2012', 'all+the+presidents+men+1976', 'monty+python+and+the+holy+grail+1975', 'the+imitation+game+2014', 'harry+potter+and+the+goblet+of+fire+2005', 'avatar+2009', '2001+a+space+odyssey+1968', 'the+green+mile+1999', 'leon+the+professional+1994', 'gone+girl+2014', 'se7en+1995', 'the+terminator+1984', 'batman+begins+2005', 'goodfellas+1990', 'whiplash+2014', 'howls+moving+castle+2004', 'harry+potter+and+the+philosophers+stone+2001', 'gladiator+2000', 'iron+man+2008', 'monsters_+inc.+2001', 'terminator+2+judgment+day+1991', 'big+hero+6+2014', 'harry+potter+and+the+half-blood+prince+2009', 'blade+runner+1982', 'pirates+of+the+caribbean+the+curse+of+the+black+pearl+2003', 'harry+potter+and+the+deathly+hallows+part+1+2010', 'one+flew+over+the+cuckoos+nest+1975', 'the+avengers+2012', 'harry+potter+and+the+chamber+of+secrets+2002', 'saving+private+ryan+1998', 'seven+samurai+1954', 'the+good_+the+bad+and+the+ugly+1966', 'forrest+gump+1994', 'spirited+away+2001', 'raiders+of+the+lost+ark+1981', 'the+matrix+1999', 'the+dark+knight+rises+2012', 'the+lord+of+the+rings+the+two+towers+2002', 'star+wars+1977', 'fight+club+1999', 'the+dark+knight+2008', 'pulp+fiction+1994', 'the+lord+of+the+rings+the+return+of+the+king+2003', 'interstellar+2014', 'inception+2010', 'the+lord+of+the+rings+the+fellowship+of+the+ring+2001']
logs = open("logfile_backup.txt", "r").readlines()
movie_count = defaultdict(int)
ratings = defaultdict(list)
recommendation_count = defaultdict(int)
count = 0

for line in logs:
    if "recommendation request" in line:
        recommendations = line[line.find("result:")+8:].split(",")[:-1]
        for rec in recommendations:
            recommendation_count[rec.strip()] += 1
    else:
        try:
            splitter = line.strip().split(" ")[1].split("/")
            if len(splitter) > 3:
                movie = splitter[-2]
                movie_count[movie] += 1
            elif len(splitter) == 3:
                item = splitter[-1]
                movie_item, rating = item.split("=")[0], int(item.split("=")[1])
                if movie_item in crafted_movies or movie_item in movies:
                    ratings[movie_item].append(rating)
        except:
            count += 1

sorted_dict = dict(sorted(movie_count.items(), key=lambda x: x[1]))
recommendation_count = dict(sorted(recommendation_count.items(), key=lambda x: -x[1]))

crafted_movies = []
for elem in sorted_dict:
    if elem not in movies and sorted_dict[elem] > 10000:
        crafted_movies.append(elem)
print(crafted_movies)
print(sorted_dict)
print(count, movies, len(logs))
for movie in recommendation_count:
    print(movie, sorted_dict[movie], recommendation_count[movie])


print(len(logs))
print(len(logs))
bins = defaultdict(dict)
for line in logs[:50000000]:
    if "recommendation request" not in line:
        splitter = line.strip().split(" ")[1].split("/")
        timer = line.strip().split(",")[0].split('T')[0].strip()
        if len(splitter) > 3:
            movie = splitter[-2]
            if movie in crafted_movies or movie in movies:
                bins[movie][timer] = bins[movie].get(timer, 0) + 1

print(bins)

import matplotlib.pyplot as plt
plt.plot(list(bins['rashomon+1950'].keys()), bins['rashomon+1950'].values(), color='maroon', linestyle='--', marker='o')
plt.plot(list(bins['the+shawshank+redemption+1994'].keys()), bins['the+shawshank+redemption+1994'].values(), color='maroon', linestyle='--', marker='o')
plt.plot(list(bins['the+apartment+1960'].keys()), bins['the+apartment+1960'].values(), color='maroon', linestyle='--', marker='o')


plt.xlabel("Dates")
plt.ylabel("Cumulative Recommendation count (in Millions)")
plt.title("Recommendation count vs Dates")
plt.xticks(rotation=45)
# plt.grid(True)
plt.show()