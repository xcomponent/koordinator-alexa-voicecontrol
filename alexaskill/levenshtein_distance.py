def levenshtein_distance(s, t):
    """
        iterative_levenshtein(s, t) -> ldist
        ldist is the Levenshtein distance between the strings
        s and t.
        For all i and j, dist[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t
    """
    rows = len(s) + 1
    cols = len(t) + 1
    dist = [[0 for x in range(cols)] for x in range(rows)]
    # source prefixes can be transformed into empty strings
    # by deletions:
    for i in range(1, rows):
        dist[i][0] = i
    # target prefixes can be created from an empty source string
    # by inserting the characters
    for i in range(1, cols):
        dist[0][i] = i

    for col in range(1, cols):
        for row in range(1, rows):
            if s[row - 1].lower() == t[col - 1].lower():  # I added lower in order not to count
                                        # the difference between a lowercase and uppercase character
                cost = 0
            else:
                cost = 1
            dist[row][col] = min(dist[row - 1][col] + 1,  # deletion
                                 dist[row][col - 1] + 1,  # insertion
                                 dist[row - 1][col - 1] + cost)  # substitution
    # for r in range(rows):
        # print(dist[r])

    return dist[row][col]


def common_characters(ch1, ch2):
    l1 = len(ch1)
    l2 = len(ch2)

    common_carac = 0
    if l1 < l2:
        for c in ch1:
            if c in ch2:
                common_carac = common_carac + 1
    else:
        for c in ch2:
            if c in ch1:
                common_carac = common_carac + 1

    return common_carac

