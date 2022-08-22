from islenska import Bin


def get_nominative_name(name: str) -> list:
    """Retrieves nominative forms of Icelandic names. Returns word forms
    unchanged where no lookup form exist, e.g. for family surnames. Returns
    multiple possible names where more than one nominative form exists, e.g.
    'Birni Jónssyni' could mean 'Björn Jónsson' or 'Birnir Jónsson.' """

    b = Bin()
    first_name_candidates = []
    latter_name_candidates = []
    candidates = []

    if len(name.split()) == 1:
        if len(b.lookup_lemmas_and_cats(name)) == 0:
            first_name_candidates.append(name)
        else:
            for first_name_candidate in b.lookup_lemmas_and_cats(name):
                first_name_candidates.append(first_name_candidate[0])
    else:
        if len(b.lookup_lemmas_and_cats(name.split()[0])) == 0:
            first_name_candidates.append(name.split()[0])
        else:
            for first_name_candidate in b.lookup_lemmas_and_cats(name.split()[0]):
                first_name_candidates.append(first_name_candidate[0])

        for latter_name in name.split()[1:]:
            if len(b.lookup_lemmas_and_cats(latter_name)) == 0:
                latter_name_candidates.append(latter_name)
            else:
                for latter_name_candidate in b.lookup_lemmas_and_cats(latter_name):
                    latter_name_candidates.append(latter_name_candidate[0])

    if len(latter_name_candidates) == 0:
        return first_name_candidates
    else:
        for first_name_candidate in first_name_candidates:
            name = first_name_candidate + ' ' + ' '.join(latter_name_candidates)
            candidates.append(name)

    return candidates
