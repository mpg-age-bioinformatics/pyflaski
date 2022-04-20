from fuzzywuzzy import process


def fuzzy_search(query_value,available_values):
    x=query_value.split(",")
    x=" ".join(x)
    x=x.split(" ")
    x=[s for s in x if len(s) > 0 ]
    x.sort()
    found_values=[ s for s in x if s in available_values ]
    not_found_values=[ s for s in x if s not in found_values ]
    best_matches={}
    for not_found in not_found_values:
        if "*" in not_found:
            not_found_=not_found.split("*")[0]
            best_match=[ s for s in available_values if s.startswith(not_found_) ]
            found_values=found_values+best_match
        else:
            #best_match=process.extractOne(gene_name,available_gene_names)[0]
            best_match=process.extract(not_found,available_values)
            if not_found.lower() == best_match[0][0].lower():
                found_values.append(best_match[0][0])
            else:
                best_match=best_match[:3]
                best_match=[ s[0] for s in best_match ]
                best_matches[not_found]=", ".join(best_match)
    if len(list(best_matches.keys())) > 0:
        emsg="The folowing values could not be found. Please consider the respective options: "
        for missing in list(best_matches.keys()):
            emsg=emsg+missing+": "+best_matches[missing]+"; "
        emsg=emsg[:-2]+"."
    else:
        emsg=None
    return found_values, emsg