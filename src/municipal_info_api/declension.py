from islenska import Bin
import itertools

NOMINATIVE_SG = 'NFET'
ACCUSATIVE_SG = 'ÞFET'
DATIVE_SG = 'ÞGFET'
GENITIVE_SG = 'EFET'
NOMINATIVE_PL = 'NFFT'
ACCUSATIVE_PL = 'ÞFFT'
DATIVE_PL = 'ÞGFFT'
GENITIVE_PL = 'EFFT'

FEM = 'kvk'
MALE = 'kk'
UNKNOWN = 'unknown'
GENDERS = [FEM, MALE]

# TODO: should we create a class where the Bin() object can live? As for now a new Bin() is created each time
# TODO: a public method in this script is called.


def get_nominative_and_gender(name: str) -> list:
    """Retrieves nominative forms of Icelandic names. Returns word forms unchanged where no lookup form exist,
    e.g. for family surnames. Returns multiple possible names where more than one nominative form exists, e.g.
    'Birni Jónssyni' could mean 'Björn Jónsson' or 'Birnir Jónsson.' Returns a list of dicts where each dict is
    on the form:
        { name: <name_candidate>,
          gender: <gender> }
    Where gender is kk (male) or kvk (female)"""

    # Make sure that name is in title case
    name = name.title()
    gender_dict = {}
    name_candidates = generate_candidates(gender_dict, name)

    # Make possible combinations of names.
    name_candidates = list(itertools.product(*name_candidates))
    return_list = create_name_gender_tuples(gender_dict, name_candidates)

    return return_list


def get_nominative_name(name: str) -> list:
    """Retrieves nominative forms of Icelandic names. Returns word forms unchanged where neither a BÍN-lookup exists
    nor a generated nominative based on the ending (e.g. 'dóttur', 'syni').
    Returns multiple possible names where more than one nominative form exists, e.g.
    'Birni Jónssyni' could mean 'Björn Jónsson' or 'Birnir Jónsson.' """

    b = Bin()
    first_name_candidates = []
    latter_name_candidates = []
    candidates = []
    name_arr = name.split()

    bin_candidates = b.lookup_lemmas_and_cats(name_arr[0].title())
    if len(bin_candidates) == 0:
        first_name, g = extract_nominative_unknown_candidate(name_arr[0])
        first_name_candidates.append(first_name)
    else:
        for first_name_candidate in bin_candidates:
            first_name_candidates.append(first_name_candidate[0])

    if len(name_arr) > 1:
        for latter_name in name_arr[1:]:
            bin_candidates = b.lookup_lemmas_and_cats(latter_name)
            if len(bin_candidates) == 0:
                latter_name, g = extract_nominative_unknown_candidate(latter_name)
                latter_name_candidates.append(latter_name)
            else:
                for latter_name_candidate in bin_candidates:
                    latter_name_candidates.append(latter_name_candidate[0])

    if len(latter_name_candidates) == 0:
        return first_name_candidates
    else:
        for first_name_candidate in first_name_candidates:
            name = first_name_candidate + ' ' + ' '.join(latter_name_candidates)
            candidates.append(name)

    return candidates


def extract_nominative_unknown_candidate(name: str) -> tuple:
    """Generate a canditate for a name not in BÍN. If we have a patro-/matronym we can deduce form and
    gender from 'son'/'dóttir', otherwise we have to leave the name as is and add gender 'unknown'.
    Return a tuple ('name_nominative', 'gender)"""

    if name.endswith('dóttir') or name.endswith('dóttur'):
        nominative = name.replace('dóttur', 'dóttir')
        gender = FEM
    elif name.endswith('son') or name.endswith('syni') or name.endswith('sonar'):
        nominative = name.replace('syni', 'son')
        nominative = nominative.replace('sonar', 'son')
        gender = MALE
    else:
        nominative = name
        gender = UNKNOWN

    return nominative, gender


def create_name_gender_tuples(gender_dict: {}, name_candidates: list) -> list:
    """name_candidates is a list of tuples of the form [(first_name1, family_name), (first_name2, family_name)] where
    e.g. we can have different first names as a result of a BÍN-lookup, each combined with the family name (of which
    we are less likely to get different versions from BÍN). Create tuples of names with a gender label and
    make sure the labels are identical for each element. If not and we have more than one tuple, discard the
    name where the elements have different genders (the BÍN-lookup might have returned entries of different genders).
    Return list is a list of dictionaries with full names and genders:
    [{name: <full-name1>,
     gender: <gender>},
     {name: <full-name2>,
     gender: <gender>},
     ...]"""

    dict_list = []
    for name_candidate_list in name_candidates:
        non_matching_genders = False
        tmp_dict = {"name": "", "gender": UNKNOWN}
        for name_part in name_candidate_list:
            if gender_dict[name_part] in GENDERS:
                if tmp_dict["gender"] == UNKNOWN or tmp_dict["gender"] == gender_dict[name_part]:
                    tmp_dict["gender"] = gender_dict[name_part]
                else:
                    # previous name element has another gender label than the current element
                    non_matching_genders = True

        # if we have the choice, leave out names with non-matching genders, probably a non-relevant retrieval from BÍN
        if len(name_candidates) > 1 and non_matching_genders:
            continue
        else:
            tmp_dict["name"] = ' '.join(name_candidate_list)
            dict_list.append(tmp_dict)

    return dict_list


def generate_candidates(gender_dict: dict, name: str) -> list:
    """Generate candidates in nominative with gender label for 'name'. First, perform a BÍN-lookup, if
    that is not successful, call extract_unknown_candidate which will either convert a patro-/matronym
    into nominative or return the name as is with gender labeled 'unknown'.
    'name' might be a full name, in which case we iterate through each element of the name (first name(s),
    family name)"""

    b = Bin()
    name_candidates = []
    for name_part in name.split(' '):
        name_part_candidates = []
        bin_candidates = b.lookup_lemmas_and_cats(name_part.title())
        if not bin_candidates:
            candidate_tuple = extract_nominative_unknown_candidate(name_part.title())
            name_part_candidates.append(candidate_tuple[0])
            gender_dict[candidate_tuple[0]] = candidate_tuple[1]
        else:
            for candidate in bin_candidates:
                name_part_candidates.append(candidate[0])
                gender_dict[candidate[0]] = candidate[1]

        name_candidates.append(name_part_candidates)
    return name_candidates


def get_declined_form(name: str, form: str) -> str:
    """Retrieves the form 'form' for 'name'. The parameter might consist of given name(s) and surname or only
     one name. Return a string with the name in the given form, or, if not found, the original name. """

    candidates = []
    name_arr = name.split()
    if len(name_arr) == 1:
        return get_form(name, form)
    else:
        for n in name_arr:
            candidates.append(get_form(n, form))

    return ' '.join(candidates)


def get_form(token: str, form: str) -> str:
    """Return the correct word form of 'token' according to 'form'.
    TODO: is this sufficient or are we likely to get multiple results here? """
    b = Bin()
    w, attr = b.lookup(token.title())
    lemma_id = attr[0].bin_id
    bin_entry = b.lookup_id(lemma_id)
    for entry in bin_entry:
        if entry.mark == form:
            return entry.bmynd
    return token


def main():
    names_and_gender = get_nominative_and_gender('sævari Blúbbidísyni')
    print(str(names_and_gender))
    accusative = get_declined_form('Sævari', ACCUSATIVE_SG)
    print(accusative)


if __name__ == '__main__':
    main()