from collections import defaultdict
from more_itertools import peekable
from colorama import Fore, Style
from prettytable import ALL, PrettyTable
from aho_corasick import AhoCorasickAutomaton


def test(corpus_file_path, input_file_path):
    print(Style.BRIGHT)

    strings = read_corpus(corpus_file_path)
    text = read_input_text(input_file_path)

    dfa = construct_dfa(strings)

    print(Fore.YELLOW + 'Searching for matching strings in text...\n\n' + Fore.RESET)

    matched_strings = peekable(dfa.search(text))

    if matched_strings.peek(None) is None:
        print(Fore.RED + 'Status: REJECTED (No matched string found)\n\n' + Fore.RESET)
        return

    print(Fore.GREEN + 'Status: ACCEPTED\n\n' + Fore.RESET)

    generate_results(matched_strings, text)

    print(Style.RESET_ALL)


def read_corpus(corpus_file_path):
    with open(f'../data/corpus/{corpus_file_path}', encoding="utf8") as file:
        strings = file.readlines()

    print(Fore.YELLOW + 'Text Corpus (String Patterns):\n\n' + Fore.RESET)

    for string in strings:
        print(string)

    strings = list(map(str.strip, strings))
    return strings


def read_input_text(input_file_path):
    with open(f'../data/input/{input_file_path}', encoding="utf8") as file:
        text = file.read()

    print(Fore.YELLOW + 'Input Text:\n\n' + Fore.RESET)
    print(text + '\n\n')

    return text


def construct_dfa(strings):
    dfa = AhoCorasickAutomaton()

    print(Fore.YELLOW + 'Constructing DFA...\n\n' + Fore.RESET)

    for string in strings:
        dfa.add(string)

    dfa.finalize()

    print(Fore.YELLOW + 'Finished constructing DFA...\n\n' + Fore.RESET)

    return dfa


def generate_results(matched_strings, text):
    colorized_text = text
    stats = defaultdict(lambda: {
        "count": 0,
        "positions": []
    })

    # Reverse the matched strings to colorize the text from the end,
    # ensuring correct coloring of matched strings
    for matched_string in reversed(list(matched_strings)):
        string = matched_string["value"]
        start = matched_string["start"]
        end = matched_string["end"]

        colorized_text = colorized_text[:start] + Fore.GREEN + \
            colorized_text[start:end] + Fore.RESET + colorized_text[end:]

        stats[string]["count"] += 1
        stats[string]["positions"].append((start, end))

    stats_table = generate_stats_table(stats)

    print(colorized_text + '\n\n')
    print(Fore.YELLOW + 'Matched Strings Statistics:\n\n' + Fore.RESET)
    print(stats_table, "\n")


def generate_stats_table(stats):
    stats_table = PrettyTable()
    stats_table.field_names = ["Matched String", "No. of Occurrences",
                               "Positions (start index: inclusive, end index: exclusive)"]
    stats_table.sortby = "Matched String"
    stats_table.hrules = ALL

    for matched_string, stat in stats.items():
        positions = map(lambda position: f'Start: {position[0]}, End: {position[1]}',
                        stat["positions"])
        stats_table.add_row([matched_string, stat["count"], "\n".join(positions)])

    return stats_table


test('names.txt', 'text-1.txt')
